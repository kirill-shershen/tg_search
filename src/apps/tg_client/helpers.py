from apps.tg_client.sessions import DjangoSession
from config.telegram import TELEGRAM_API_HASH
from config.telegram import TELEGRAM_API_ID
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError


async def login_user(client_session, phone_number, code, password, phone_code_hash):
    telegram_client = TelegramClient(DjangoSession(client_session=client_session), TELEGRAM_API_ID, TELEGRAM_API_HASH)
    await telegram_client.connect()
    try:
        await telegram_client.sign_in(phone=phone_number, code=code, phone_code_hash=phone_code_hash)
    except SessionPasswordNeededError:
        await telegram_client.sign_in(password=password)
    result = await telegram_client.is_user_authorized()
    await telegram_client.disconnect()
    return result


async def send_code_request(client_session, phone_number):
    telegram_client = TelegramClient(DjangoSession(client_session=client_session), TELEGRAM_API_ID, TELEGRAM_API_HASH)
    await telegram_client.connect()
    result = await telegram_client.send_code_request(phone_number)
    await telegram_client.disconnect()
    return result.phone_code_hash
