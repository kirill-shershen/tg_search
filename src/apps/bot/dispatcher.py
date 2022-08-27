import asyncio
from asyncio import run

from apps.bot.helpers import get_add_chat_message
from apps.bot.helpers import get_add_chat_reject_max
from apps.bot.helpers import get_start_message
from apps.bot.models import User
from apps.bot.models import UserChat
from apps.tg_client.helpers import get_bot_client
from apps.tg_client.helpers import re_connect_clients
from config.logger import logger
from config.telegram import BOT_RECONNECT_TIMER_MIN
from config.telegram import CHAT_TEXT_ADD_CHAT
from config.telegram import MAX_GROUPS_PER_USER
from telethon import Button
from telethon import events
from telethon.tl.types import PeerChat

client = get_bot_client()
client.start()


def get_keyboard():
    return [[Button.text(CHAT_TEXT_ADD_CHAT, resize=True), Button.text("➖ чат"), Button.text("🔍 поиск")]]


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
            await conversation.send_message(get_add_chat_reject_max())
            await conversation.cancel_all()
            return

        await conversation.send_message(get_add_chat_message(chat_list))
        while True:
            chat_name = await conversation.get_response()
            chat_name = chat_name.raw_text.strip()
            chat = None
            if chat_name:
                logger.debug(chat_name)
                try:
                    chat = await client.get_entity(chat_name)
                except:
                    chat = None
            if not chat:
                await conversation.send_message("try again")
            else:
                break
            await asyncio.sleep(2)
        UserChat.objects.create(user=tg_user, username=chat.username, title=chat.title, chat_id=chat.id)
        await conversation.send_message("success")
        await conversation.cancel_all()


async def healthcheck():
    while True:
        await asyncio.sleep(30)
        if not await client.is_user_authorized():
            await re_connect_clients()
            await asyncio.sleep(BOT_RECONNECT_TIMER_MIN)


def run_pooling():
    with client:
        client.loop.run_until_complete(healthcheck())
