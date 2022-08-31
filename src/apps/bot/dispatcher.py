import asyncio
import re
from typing import Union

from apps.bot.helpers import get_add_chat_message
from apps.bot.helpers import get_add_chat_reject_max
from apps.bot.helpers import get_choose_action_message
from apps.bot.helpers import get_daily_limit_message
from apps.bot.helpers import get_delete_chat_message
from apps.bot.helpers import get_exist_chat_message
from apps.bot.helpers import get_nothing_delete_message
from apps.bot.helpers import get_nowhere_search_message
from apps.bot.helpers import get_result_message
from apps.bot.helpers import get_search_message
from apps.bot.helpers import get_start_message
from apps.bot.helpers import get_wrong_chat_message
from apps.bot.models import QueryResult
from apps.bot.models import SearchQuery
from apps.bot.models import User
from apps.bot.models import UserChat
from apps.tg_client.helpers import get_bot_client
from apps.tg_client.helpers import get_client
from apps.tg_client.helpers import get_search_request
from apps.tg_client.helpers import re_connect_clients
from asgiref.sync import sync_to_async
from config.logger import logger
from config.telegram import BOT_RECONNECT_TIMER_MIN
from config.telegram import CHAT_TEXT_ADD_CHAT
from config.telegram import CHAT_TEXT_DELETE_CHAT
from config.telegram import CHAT_TEXT_SEARCH
from config.telegram import MAX_GROUPS_PER_USER
from config.telegram import MAX_REQUESTS_PER_DAY
from telethon import Button
from telethon import events


client = get_bot_client()
client.start()
search_client = get_client()


def press_event(user_id):
    return events.CallbackQuery(func=lambda e: e.sender_id == user_id)


def get_keyboard():
    return [
        [
            Button.text(CHAT_TEXT_ADD_CHAT, resize=True, single_use=False),
            Button.text(CHAT_TEXT_DELETE_CHAT, single_use=False),
            Button.text(CHAT_TEXT_SEARCH, single_use=False),
        ]
    ]


def get_del_chat_keyboard(chats: list) -> Union[list[list[Button]], None]:
    if not chats:
        return None
    else:
        return [[Button.inline(text=f"{chat.title}", data=f"del_{chat.id}")] for chat in chats]


def get_cancel_keyboard() -> list[list[Button]]:
    return [[Button.text(text="Отмена", single_use=False, resize=True)]]


async def send_choose_action(event, edit: bool = False, success: bool = False, failed: bool = False) -> None:
    if edit:
        return await event.edit_message(
            message=await get_choose_action_message(success, failed), buttons=get_keyboard()
        )
    else:
        return await event.send_message(
            message=await get_choose_action_message(success, failed), buttons=get_keyboard()
        )


async def get_tg_user(event) -> User:
    # tg_user = await get_tg_user_by_user_id(user_id=event.chat.id)
    tg_user = await User.objects.filter(user_id=event.chat.id).afirst()
    if not tg_user:
        tg_user, _ = await User.objects.aupdate_or_create(
            username=event.chat.username,
            first_name=event.chat.first_name,
            last_name=event.chat.last_name,
            user_id=event.chat.id,
            phone=event.chat.phone,
        )
    return tg_user


# @client.on(events.CallbackQuery(data=re.compile(r"cancel_(\d*)")))
# async def handler(event):
#     user_id = int(event.data_match.group(1))
#     if not user_id:
#         event.edit("something went wrong", buttons=[])
#         return
#     if user_id == event.sender_id:
#         await client.send_message(entity=event.chat_id, message="Добавление чата было прервано", buttons=get_keyboard())


@events.register(events.CallbackQuery(data=re.compile(r"del_(\d*)")))
async def callback_del(event):
    chat_id = int(event.data_match.group(1))
    if not chat_id:
        return await send_choose_action(event, edit=True, failed=True)

    try:
        user_chat = await UserChat.objects.select_related("user").aget(pk=chat_id)
    except BaseException:
        return await send_choose_action(event, edit=True, failed=True)

    user = user_chat.user
    if user.user_id == event.sender_id:
        await sync_to_async(user_chat.delete)()
        chat_list = await sync_to_async(list)(UserChat.objects.filter(user=user))
        keyboard = get_del_chat_keyboard(chats=chat_list)
        if keyboard:
            await event.edit(await get_delete_chat_message(), buttons=keyboard, parse_mode="html")
        else:
            await send_choose_action(event, edit=True)


@events.register(events.NewMessage(pattern="/start"))
async def start(event):
    if not event.chat.bot:
        tg_user = await get_tg_user(event)
        await event.client.send_message(
            entity=event.chat_id, message=await get_start_message(tg_user.name), buttons=get_keyboard()
        )


@events.register(events.NewMessage(pattern=CHAT_TEXT_SEARCH))
async def search(event):
    async with event.client.conversation(event.chat) as conversation:
        tg_user = await get_tg_user(event)
        # check for chat exist
        chat_list = await sync_to_async(list)(UserChat.objects.filter(user=tg_user))
        if len(chat_list) == 0:
            await conversation.send_message(message=await get_nowhere_search_message())
            return conversation.cancel()
        # check for request limit
        today_requests: list = await sync_to_async(list)(SearchQuery.objects.today())
        requests_per_day_left = MAX_REQUESTS_PER_DAY - len(today_requests)
        if requests_per_day_left == 0:
            await event.respond(message=await get_daily_limit_message(), buttons=get_keyboard())
            return conversation.cancel()

        await conversation.send_message(
            await get_search_message(chat_list=chat_list, request_count=requests_per_day_left),
            buttons=get_cancel_keyboard(),
        )
        while True:
            try:
                search_request = await conversation.get_response()
            except asyncio.exceptions.TimeoutError:
                continue
            search_request = search_request.message.strip()
            if search_request.lower() == "отмена":
                await send_choose_action(event=conversation)
                return conversation.cancel()
            else:
                break

        query_search = await SearchQuery.objects.acreate(user=tg_user, query=search_request)
        results = await get_search_request(client=search_client, query=search_request, chats=chat_list)
        await QueryResult.objects.abulk_create([QueryResult(query=query_search, **result) for result in results])
        # telegram message limit 4096
        message = await get_result_message(messages=results, query=search_request)
        await conversation.send_message(message=message[:4096], buttons=get_keyboard(), parse_mode="html")
        conversation.cancel()


@events.register(events.NewMessage(pattern=CHAT_TEXT_ADD_CHAT))
async def add_chat(event):
    async with event.client.conversation(event.chat) as conversation:
        tg_user = await get_tg_user(event)

        chat_list = await sync_to_async(list)(UserChat.objects.filter(user=tg_user))
        if len(chat_list) >= MAX_GROUPS_PER_USER:
            await conversation.cancel()
            return await conversation.send_message(await get_add_chat_reject_max(), buttons=get_keyboard())

        await conversation.send_message(await get_add_chat_message(chat_list), buttons=get_cancel_keyboard())
        while True:
            try:
                chat_name = await conversation.get_response()
            except asyncio.exceptions.TimeoutError:
                continue
            chat_name = chat_name.message.strip()
            if chat_name.lower() == "отмена":
                await send_choose_action(event=conversation)
                return conversation.cancel()
            if chat_name:
                try:
                    chat = await event.client.get_entity(chat_name)
                except Exception as e:
                    logger.error(f"get_entity error: {str(e)}")
                    chat = None
            if not chat:
                await event.respond(await get_wrong_chat_message(), buttons=get_cancel_keyboard())
                continue
            else:
                break

        user_chat, created = await UserChat.objects.aget_or_create(
            user=tg_user, username=chat.username, title=chat.title, chat_id=chat.id
        )
        if not created:
            await conversation.send_message(await get_exist_chat_message(chat=user_chat.title), buttons=get_keyboard())
        else:
            await send_choose_action(event=conversation, success=True)
        conversation.cancel()


@events.register(events.NewMessage(pattern=CHAT_TEXT_DELETE_CHAT))
async def delete_chat(event):
    tg_user = await get_tg_user(event)
    chat_list = await sync_to_async(list)(UserChat.objects.filter(user=tg_user))
    if len(chat_list) == 0:
        await event.client.send_message(entity=event.chat_id, message=await get_nothing_delete_message())
        return
    keyboard = get_del_chat_keyboard(chats=chat_list)
    await event.client.send_message(
        entity=event.chat_id, message=await get_delete_chat_message(), buttons=keyboard, parse_mode="html"
    )


async def main():

    await client.connect()
    for f in (start, callback_del, add_chat, delete_chat, search):
        client.add_event_handler(f)
    while True:
        await asyncio.sleep(30)
        if not await client.is_user_authorized():
            await re_connect_clients()
            await asyncio.sleep(BOT_RECONNECT_TIMER_MIN)


def run_pooling():
    # asyncio.run(main())
    asyncio.get_event_loop().run_until_complete(main())
