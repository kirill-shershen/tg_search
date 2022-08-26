import asyncio

from apps.tg_client.helpers import get_bot_client
from apps.tg_client.helpers import get_client
from config.logger import logger
from config.telegram import BOT_RECONNECT_TIMER_MIN
from telethon import Button
from telethon import events

client = get_bot_client()
client.start()


def get_keyboard():
    return [[Button.text("➕ чат", resize=True), Button.text("➖ чат"), Button.text("🔍 поиск")]]


@client.on(events.NewMessage(pattern="/start"))
async def start(event):
    await client.send_message(event.chat_id, "hey", buttons=get_keyboard())


def run_pooling():
    client.run_until_disconnected()
