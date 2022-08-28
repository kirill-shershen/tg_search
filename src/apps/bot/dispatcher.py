import asyncio
import re
from typing import Union

from apps.bot.helpers import get_add_chat_message
from apps.bot.helpers import get_add_chat_reject_max
from apps.bot.helpers import get_delete_chat_message
from apps.bot.helpers import get_start_message
from apps.bot.models import User
from apps.bot.models import UserChat
from apps.tg_client.helpers import get_bot_client
from apps.tg_client.helpers import re_connect_clients
from config.logger import logger
from config.telegram import BOT_RECONNECT_TIMER_MIN
from config.telegram import CHAT_TEXT_ADD_CHAT
from config.telegram import CHAT_TEXT_DELETE_CHAT
from config.telegram import MAX_GROUPS_PER_USER
from telethon import Button
from telethon import events

client = get_bot_client()
client.start()


def press_event(user_id):
    return events.CallbackQuery(func=lambda e: e.sender_id == user_id)


def get_keyboard():
    return [
        [
            Button.text(CHAT_TEXT_ADD_CHAT, resize=True, single_use=False),
            Button.text(CHAT_TEXT_DELETE_CHAT, single_use=False),
            Button.text("🔍 поиск", single_use=False),
        ]
    ]


def get_del_chat_keyboard(chats: list) -> Union[list[list[Button]], None]:
    if not chats:
        return None
    else:
        return [[Button.inline(text=f"{chat.title}", data=f"del_{chat.id}")] for chat in chats]


def get_cancel_keyboard() -> list[list[Button]]:
    return [[Button.text(text="Отмена", single_use=False, resize=True)]]


def get_tg_user(event) -> User:
    tg_user = User.objects.filter(user_id=event.chat.id).first()
    if not tg_user:
        tg_user, _ = User.objects.update_or_create(
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


@client.on(events.CallbackQuery(data=re.compile(r"del_(\d*)")))
async def handler(event):
    chat_id = int(event.data_match.group(1))
    if not chat_id:
        event.edit("something went wrong", buttons=[])
        return

    user_chat = UserChat.objects.get_or_none(pk=chat_id)
    if not user_chat:
        return

    user = user_chat.user
    if user.user_id == event.sender_id:
        user_chat.delete()
        chat_list = UserChat.objects.filter(user=user)
        keyboard = get_del_chat_keyboard(chats=chat_list)
        if keyboard:
            await event.edit(get_delete_chat_message(), buttons=keyboard, parse_mode="html")
        else:
            await event.edit("Выберите действие", buttons=get_keyboard())


@client.on(events.NewMessage(pattern="/start"))
async def start(event):
    if not event.chat.bot:
        tg_user = get_tg_user(event)
        await client.send_message(entity=event.chat_id, message=get_start_message(tg_user.name), buttons=get_keyboard())


@client.on(events.NewMessage(pattern=CHAT_TEXT_ADD_CHAT))
async def add_chat(event):
    async with client.conversation(event.chat) as conversation:
        tg_user = get_tg_user(event)

        chat_list = UserChat.objects.filter(user=tg_user)
        if len(chat_list) >= MAX_GROUPS_PER_USER:
            await conversation.send_message(get_add_chat_reject_max(), buttons=get_keyboard())
            await conversation.cancel_all()
            return

        await conversation.send_message(get_add_chat_message(chat_list), buttons=get_cancel_keyboard())
        while True:
            try:
                chat_name = await conversation.get_response()
            except TimeoutError:
                await conversation.cancel()
                return await event.respond("Выберите действие", buttons=get_keyboard())
            chat_name = chat_name.message.strip()
            if chat_name.lower() == "отмена":
                return await event.respond("Выберите действие", buttons=get_keyboard())
            if chat_name:
                logger.debug(f"{chat_name=}")
                try:
                    chat = await client.get_entity(chat_name)
                except Exception as e:
                    logger.error(f"get_entity error {str(e)}")
                    chat = None
            if not chat:
                await conversation.send_message("chat is wrong. try again", buttons=get_cancel_keyboard())
                continue
            else:
                break

        user_chat, created = UserChat.objects.get_or_create(
            user=tg_user, username=chat.username, title=chat.title, chat_id=chat.id
        )
        if not created:
            await conversation.send_message(f"'{user_chat.title}' chat already exist", buttons=get_keyboard())
        else:
            await event.respond("Выберите действие", buttons=get_keyboard())
        await conversation.cancel()


@client.on(events.NewMessage(pattern=CHAT_TEXT_DELETE_CHAT))
async def delete_chat(event):
    chat_list = UserChat.objects.filter(user=get_tg_user(event))
    if len(chat_list) == 0:
        await client.send_message(entity=event.chat_id, message="Nothing to delete")
        return
    keyboard = get_del_chat_keyboard(chats=chat_list)
    await client.send_message(
        entity=event.chat_id, message=get_delete_chat_message(), buttons=keyboard, parse_mode="html"
    )


async def healthcheck():
    while True:
        await asyncio.sleep(30)
        if not await client.is_user_authorized():
            await re_connect_clients()
            await asyncio.sleep(BOT_RECONNECT_TIMER_MIN)


def run_pooling():
    with client:
        client.loop.run_until_complete(healthcheck())
