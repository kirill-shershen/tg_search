import logging

from apps.tg_client.models import ClientSession
from apps.tg_client.models import LoginStatus
from apps.tg_client.sessions import DjangoSession
from config.telegram import CLIENT_SESSION_BOT
from config.telegram import CLIENT_SESSION_SEARCH
from config.telegram import TELEGRAM_API_HASH
from config.telegram import TELEGRAM_API_ID
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError


async def get_client(client_session: ClientSession = None) -> TelegramClient:
    """Get TelegramClient with the custom session or the default search session."""
    if not client_session:
        client_session = ClientSession.objects.filter(name=CLIENT_SESSION_SEARCH).first()
    return TelegramClient(DjangoSession(client_session=client_session), TELEGRAM_API_ID, TELEGRAM_API_HASH)  # type: ignore


async def get_bot_client() -> TelegramClient:
    return await get_client(client_session=ClientSession.objects.filter(name=CLIENT_SESSION_BOT).first())


async def login_user(
    client_session: ClientSession, phone_number: str, code: int, password: str, phone_code_hash: str
) -> bool:
    """Do sign-in on telegram using received code and hash."""
    telegram_client = await get_client(client_session=client_session)
    await telegram_client.connect()
    try:
        await telegram_client.sign_in(phone=phone_number, code=code, phone_code_hash=phone_code_hash)
    except SessionPasswordNeededError:
        await telegram_client.sign_in(password=password)
    result = await telegram_client.is_user_authorized()
    await telegram_client.disconnect()
    return result


async def login_bot(client_session: ClientSession, bot_token: str) -> bool:
    """Do sign-in bot on telegram using bot_token."""
    telegram_client = await get_client(client_session=client_session)
    await telegram_client.connect()
    await telegram_client.sign_in(bot_token=bot_token)
    result = await telegram_client.is_user_authorized()
    await telegram_client.disconnect()
    return result


async def logout_user(client_session: ClientSession) -> str:
    """Do log-out from telegram."""
    telegram_client = await get_client(client_session=client_session)
    await telegram_client.connect()
    await telegram_client.log_out()
    return "OK"


async def send_code_request(client_session: ClientSession, phone_number: str) -> str:
    """Send code request"""
    telegram_client = await get_client(client_session=client_session)
    await telegram_client.connect()
    result = await telegram_client.send_code_request(phone_number)
    await telegram_client.disconnect()
    return result.phone_code_hash


async def connect_client(client_session: ClientSession) -> None:
    telegram_client = await get_client(client_session=client_session)
    await telegram_client.connect()
    if not await telegram_client.is_user_authorized():
        client_session.login_status = LoginStatus.LOGIN_REQUIRED
        client_session.save()
        logging.critical(f"Authorization failed for client: {client_session.name}")
        return
    if client_session.login_status != LoginStatus.LOGIN_DONE:
        client_session.login_status = LoginStatus.LOGIN_DONE
        client_session.save()


async def re_connect_clients() -> None:
    telegram_client = await get_client()
    await telegram_client.connect()
