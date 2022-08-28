from typing import Optional

from apps.tg_client.models import ClientSession
from apps.tg_client.models import Login
from apps.tg_client.models import LoginStatus
from apps.tg_client.sessions import DjangoSession
from config.logger import logger
from config.telegram import CLIENT_SESSION_BOT
from config.telegram import CLIENT_SESSION_SEARCH
from config.telegram import MAX_ANSWERS_PER_REQUEST
from config.telegram import TELEGRAM_API_HASH
from config.telegram import TELEGRAM_API_ID
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl import functions
from telethon.tl import types
from telethon.tl.types import InputPeerChat
from telethon.tl.types import InputPeerEmpty
from telethon.tl.types import User


def get_client(client_session: ClientSession = None) -> TelegramClient:
    """Get TelegramClient with the custom session or the default search session."""
    if not client_session:
        client_session = ClientSession.objects.filter(name=CLIENT_SESSION_SEARCH).first()
    return TelegramClient(DjangoSession(client_session=client_session), TELEGRAM_API_ID, TELEGRAM_API_HASH)  # type: ignore


def get_bot_client() -> TelegramClient:
    return get_client(client_session=ClientSession.objects.filter(name=CLIENT_SESSION_BOT).first())


async def login_user(
    client_session: ClientSession, phone_number: str, code: int, password: str, phone_code_hash: str
) -> bool:
    """Do sign-in on telegram using received code and hash."""
    telegram_client = get_client(client_session=client_session)
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
    telegram_client = get_client(client_session=client_session)
    await telegram_client.connect()
    await telegram_client.sign_in(bot_token=bot_token)
    result = await telegram_client.is_user_authorized()
    await telegram_client.disconnect()
    return result


async def logout_user(client_session: ClientSession) -> str:
    """Do log-out from telegram."""
    telegram_client = get_client(client_session=client_session)
    await telegram_client.connect()
    await telegram_client.log_out()
    return "OK"


async def send_code_request(client_session: ClientSession, phone_number: str) -> str:
    """Send code request"""
    telegram_client = get_client(client_session=client_session)
    await telegram_client.connect()
    result = await telegram_client.send_code_request(phone_number)
    await telegram_client.disconnect()
    return result.phone_code_hash


async def connect_client(client_session: ClientSession) -> None:
    telegram_client = get_client(client_session=client_session)
    await telegram_client.connect()
    if not await telegram_client.is_user_authorized():
        client_session.login_status = LoginStatus.LOGIN_REQUIRED
        client_session.save()
        logger.critical(f"Authorization failed for client: {client_session.name}")
        return
    if client_session.login_status != LoginStatus.LOGIN_DONE:
        client_session.login_status = LoginStatus.LOGIN_DONE
        client_session.save()


async def re_connect_clients() -> None:
    for login in Login.objects.filter(have_to_send_code=True):
        phone_hash = await send_code_request(login.client_session, login.phone_number)
        login.hash_code = phone_hash
        login.have_to_send_code = False
        login.save()
    for login in Login.objects.filter(code__isnull=False):
        if login.bot_token:
            login_result = await login_bot(login.client_session, login.bot_token)
        else:
            login_result = await login_user(
                login.client_session, login.phone_number, login.code, login.passcode, login.hash_code
            )
        if login_result:
            login.client_session.login_status = LoginStatus.LOGIN_WAITING_FOR_TELEGRAM_CLIENT
            login.client_session.save()
            logger.debug(f"Login successfully for client: {login.client_session.name}")
        else:
            logger.debug(f"Login failed for client: {login.client_session.name}")
        for client in ClientSession.objects.filter(login_status=LoginStatus.LOGIN_WAITING_FOR_TELEGRAM_CLIENT):
            await connect_client(client_session=client)


async def normalize_results(client: TelegramClient, results: list) -> list:
    if not results:
        return []

    messages = []
    if len(results) == 1:
        for message in results[0].messages:
            logger.debug(f"{message=}")
            user_info = await client.get_entity(message.from_id)
            user = user_info.username if user_info.username else user_info.first_name
            messages.append(
                {
                    "message_date": message.date,
                    "from_user_name": user,
                    "from_user_id": user_info.id,
                    "message": message.message,
                }
            )
    return messages


async def get_search_request(query: str, chats: list) -> list:
    telegram_client = get_client()
    await telegram_client.start()
    results = []
    for chat in chats:
        results.append(
            await telegram_client(
                functions.messages.SearchRequest(
                    filter=types.InputMessagesFilterEmpty(),
                    peer=chat.username,
                    q=query,
                    min_date=None,
                    max_date=None,
                    offset_id=0,
                    add_offset=0,
                    limit=MAX_ANSWERS_PER_REQUEST,
                    max_id=0,
                    min_id=0,
                    hash=0,
                    from_id=InputPeerEmpty(),
                    top_msg_id=0,
                )
            )
        )
    results = await normalize_results(client=telegram_client, results=results)

    await telegram_client.disconnect()
    return results
