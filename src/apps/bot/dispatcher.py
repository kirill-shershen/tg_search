import asyncio
import re

from apps.bot.helpers import get_add_chat_message
from apps.bot.helpers import get_add_chat_reject_max
from apps.bot.helpers import get_daily_limit_message
from apps.bot.helpers import get_exist_chat_message
from apps.bot.helpers import get_group_list_message
from apps.bot.helpers import get_help_message
from apps.bot.helpers import get_nowhere_search_message
from apps.bot.helpers import get_result_message
from apps.bot.helpers import get_search_message
from apps.bot.helpers import get_success_message
from apps.bot.helpers import get_wrong_chat_message
from apps.bot.models import QueryResult
from apps.bot.models import SearchQuery
from apps.bot.models import User
from apps.bot.models import UserChat
from apps.tg_client.helpers import get_bot_client
from apps.tg_client.helpers import get_client
from apps.tg_client.helpers import get_search_request
from apps.tg_client.helpers import reconnect_client
from asgiref.sync import sync_to_async
from config.logger import logger
from config.telegram import BOT_RECONNECT_TIMER_MIN
from config.telegram import CLIENT_SESSION_BOT
from config.telegram import CLIENT_SESSION_SEARCH
from config.telegram import MAX_GROUPS_PER_USER
from config.telegram import MAX_REQUESTS_PER_DAY
from telethon import Button
from telethon import events


client = get_bot_client()
search_client = get_client()


def get_chat_list_inline_keyboard() -> list[Button]:
    return [
        Button.inline(text="Список групп", data="group_list"),
        Button.inline(text="Добавить группу", data="add_group"),
    ]


def get_cancel_to_group_inline_keyboard() -> Button:
    return Button.inline(text="Отмена", data="group_list")


def get_cancel_to_help_inline_keyboard() -> list[Button]:
    return [Button.inline(text="Отмена", data="help")]


def get_search_inline_keyboard() -> list:
    return [get_chat_list_inline_keyboard(), get_cancel_to_help_inline_keyboard()]


def get_chat_list_keyboard(chats: list) -> list[list[Button]]:
    chat_list = [[Button.inline(text=f"{chat.title}", data=f"del_{chat.id}")] for chat in chats]
    if len(chat_list) < MAX_GROUPS_PER_USER:
        chat_list.insert(0, [Button.inline(text="Добавить группу", data="add_group")])
    chat_list.append([Button.inline(text="Поиск", data="search"), Button.inline(text="Выход", data="help")])
    return chat_list


async def get_tg_user(event) -> User:
    """get or create telegram user"""
    tg_user = await User.objects.filter(user_id=event.chat.id).afirst()
    if not tg_user:
        tg_user, _ = await User.objects.aupdate_or_create(
            username=event.chat.username,
            first_name=event.chat.first_name,
            last_name=event.chat.last_name,
            user_id=event.chat.id,
            phone=event.chat.phone,
        )
        logger.info(f"added new user {tg_user=}")
    return tg_user


async def do_search_event(event, edit: bool = False):
    async with event.client.conversation(event.chat) as conversation:
        message_event = event.edit if edit else conversation.send_message
        tg_user = await get_tg_user(event)

        # check for chat exist
        chat_list = await sync_to_async(list)(UserChat.objects.filter(user=tg_user))
        if len(chat_list) == 0:
            await message_event(await get_nowhere_search_message(), buttons=get_chat_list_inline_keyboard())
            return conversation.cancel()
        # check for limits
        requests_per_day_left = await get_requests_today_remaining(user=tg_user)
        if requests_per_day_left <= 0:
            await message_event(await get_daily_limit_message())
            return conversation.cancel()
        # dialog to search
        if edit:
            await event.delete()
        await conversation.send_message(
            await get_search_message(chat_list=chat_list, request_count=requests_per_day_left),
            buttons=get_search_inline_keyboard(),
        )
        while True:
            try:
                search_request = await conversation.get_response()
            except asyncio.exceptions.TimeoutError:
                continue
            search_request = search_request.message.strip()
            if await exit_check(
                conversation=conversation, response=search_request, requests_per_day_left=requests_per_day_left
            ):
                return

            requests_per_day_left -= 1
            message = await get_and_save_query_result(user=tg_user, request=search_request, chat_list=chat_list)
            await conversation.send_message(
                message=message,
                link_preview=False,
                parse_mode="html",
            )


async def get_group_list(event, edit=False, user: User = None):
    """show edit groups message"""
    await _force_close_all_conversation(event)
    tg_user = await get_tg_user(event) if not user else user

    chat_list = await sync_to_async(list)(UserChat.objects.filter(user=tg_user))

    message_event = event.edit if edit else event.respond
    await message_event(await get_group_list_message(), buttons=get_chat_list_keyboard(chats=chat_list))


async def get_requests_today_remaining(user: User):
    """Get daily request count remaining for user"""
    today_requests: list = await sync_to_async(list)(SearchQuery.objects.today(user=user))
    return MAX_REQUESTS_PER_DAY - len(today_requests)


async def exit_check(conversation, response: str, requests_per_day_left: int) -> bool:
    exit_status = False
    if requests_per_day_left == 0:
        await conversation.send_message(await get_daily_limit_message())
        await conversation.cancel_all()
        exit_status = True
    if response.lower() in ["отмена", "/groups", "/search"]:
        await conversation.cancel_all()
        exit_status = True

    return exit_status


async def get_and_save_query_result(user: User, request: str, chat_list: list) -> str:
    query_search = await SearchQuery.objects.acreate(user=user, query=request)
    try:
        results = await get_search_request(client=search_client, query=request, chats=chat_list)
    except Exception as e:
        return f"failed to search in group: {str(e)}"
    else:
        logger.debug(f"{results=}")
        await QueryResult.objects.abulk_create([QueryResult(query=query_search, **result) for result in results])
        return await get_result_message(
            messages=results, query=request, requests_per_day_left=await get_requests_today_remaining(user=user)
        )


async def _force_close_all_conversation(event):
    chat_id = await client.get_peer_id(event.chat_id)
    for conv in client._conversations[chat_id]:
        conv.cancel()


async def send_help_message(event, edit=False, username: str = ""):
    await _force_close_all_conversation(event)
    message_event = event.edit if edit else event.respond
    await message_event(await get_help_message(name=username))


async def send_error_message(event, edit=False):
    await _force_close_all_conversation(event)
    message_event = event.edit if edit else event.respond
    await message_event(await get_success_message())


@events.register(events.CallbackQuery(data="search"))
async def callback_search(event):
    await _force_close_all_conversation(event)
    await do_search_event(event, edit=True)


@events.register(events.CallbackQuery(data="help"))
async def callback_help(event):
    await send_help_message(event, edit=True)


@events.register(events.CallbackQuery(data="add_group"))
async def callback_group_add(event):
    async with event.client.conversation(event.chat) as conversation:
        tg_user = await get_tg_user(event)

        chat_list = await sync_to_async(list)(UserChat.objects.filter(user=tg_user))
        if len(chat_list) >= MAX_GROUPS_PER_USER:
            await event.edit(await get_add_chat_reject_max(), buttons=get_chat_list_keyboard(chats=chat_list))
            return await conversation.cancel_all()

        await event.delete()
        await conversation.send_message(
            await get_add_chat_message(chat_list), buttons=get_cancel_to_group_inline_keyboard()
        )
        while True:
            try:
                chat_name = await conversation.get_response()
            except asyncio.exceptions.TimeoutError:
                continue
            chat_name = chat_name.message.strip()
            if chat_name:
                try:
                    chat = await event.client.get_entity(chat_name)
                except Exception as e:
                    logger.error(f"get_entity error: {str(e)}")
                    chat = None
            if not chat:
                await event.respond(await get_wrong_chat_message(), buttons=get_cancel_to_group_inline_keyboard())
                continue

            user_chat, created = await UserChat.objects.aget_or_create(
                user=tg_user, username=chat.username, title=chat.title, chat_id=chat.id
            )
            if not created:
                await event.respond(
                    await get_exist_chat_message(chat=user_chat.title), buttons=get_cancel_to_group_inline_keyboard()
                )
                continue
            else:
                chat_list.append(user_chat)

                await event.respond(await get_success_message(success=True), buttons=get_chat_list_inline_keyboard())
                return await conversation.cancel_all()


@events.register(events.CallbackQuery(data="group_list"))
async def callback_group_list(event):
    return await get_group_list(event, edit=True)


@events.register(events.CallbackQuery(data=re.compile(r"del_(\d*)")))
async def callback_group_del(event):
    chat_id = int(event.data_match.group(1))
    if not chat_id:
        return await send_error_message(event, edit=True)

    try:
        user_chat = await UserChat.objects.select_related("user").aget(pk=chat_id)
    except Exception:
        return

    user = user_chat.user
    if user.user_id == event.sender_id:
        try:
            await sync_to_async(user_chat.delete)()
        finally:
            await get_group_list(event, edit=True, user=user)


@events.register(events.NewMessage(pattern="/help"))
async def help_command(event):
    await send_help_message(event)


@events.register(events.NewMessage(pattern="(?i)отмена"))
async def cancel_action(event) -> None:
    return await send_help_message(event)


@events.register(events.NewMessage(pattern="/start"))
async def start(event):
    if not event.chat.bot:
        await get_tg_user(event)
        await send_help_message(event)


@events.register(events.NewMessage(pattern="/groups"))
async def groups_command(event):
    return await get_group_list(event)


@events.register(events.NewMessage(pattern="/search"))
async def search_command(event):
    await _force_close_all_conversation(event)
    await do_search_event(event)


async def main():
    for f in (
        start,
        callback_group_del,
        cancel_action,
        search_command,
        groups_command,
        help_command,
        callback_group_add,
        callback_group_list,
        callback_help,
        callback_search,
    ):
        client.add_event_handler(f)

    while True:
        await asyncio.sleep(10)
        await client.connect()
        if not await client.is_user_authorized():
            await reconnect_client(client=CLIENT_SESSION_BOT)
            client.start()
        await search_client.connect()
        if not await search_client.is_user_authorized():
            await reconnect_client(client=CLIENT_SESSION_SEARCH)
        await asyncio.sleep(BOT_RECONNECT_TIMER_MIN)


def run_pooling():
    asyncio.get_event_loop().run_until_complete(main())
