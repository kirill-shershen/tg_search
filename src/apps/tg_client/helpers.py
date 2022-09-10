import os

import telethon
from apps.tg_client.models import ClientSession
from apps.tg_client.models import Login
from apps.tg_client.models import LoginStatus
from apps.tg_client.sessions import DjangoSession
from asgiref.sync import sync_to_async
from config.logger import logger
from config.telegram import CLIENT_SESSION_BOT
from config.telegram import CLIENT_SESSION_SEARCH
from config.telegram import MAX_ANSWERS_PER_REQUEST
from config.telegram import MAX_LENGTH_FOR_REQUEST
from config.telegram import TELEGRAM_API_HASH
from config.telegram import TELEGRAM_API_ID
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.errors import SessionPasswordNeededError
from telethon.tl import functions
from telethon.tl import types
from telethon.tl.types import InputPeerEmpty
from telethon.tl.types import PeerChannel
from telethon.tl.types.messages import ChannelMessages


def get_client(client_session: ClientSession = None, loop=None) -> TelegramClient:
    """Get TelegramClient with the custom session or the default search session."""
    if not client_session:
        client_session = ClientSession.objects.select_related("session").filter(name=CLIENT_SESSION_SEARCH).first()
    return TelegramClient(
        DjangoSession(client_session=client_session), TELEGRAM_API_ID, TELEGRAM_API_HASH, loop=loop  # type: ignore
    )


def get_bot_client() -> TelegramClient:
    return get_client(client_session=ClientSession.objects.filter(name=CLIENT_SESSION_BOT).first())


async def login_user(
    client_session: ClientSession, phone_number: str, code: int, password: str, phone_code_hash: str
) -> bool:
    """Do sign-in on telegram using received code and hash."""
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    telegram_client = get_client(client_session=client_session)
    await telegram_client.connect()
    try:
        await telegram_client.sign_in(phone=phone_number, code=code, phone_code_hash=phone_code_hash)
    except SessionPasswordNeededError:
        await telegram_client.sign_in(password=password)
    result = await telegram_client.is_user_authorized()
    await telegram_client.disconnect()
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "false"
    return result


async def login_bot(client_session: ClientSession, bot_token: str) -> bool:
    """Do sign-in bot on telegram using bot_token."""
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    telegram_client = get_client(client_session=client_session)
    await telegram_client.connect()
    await telegram_client.sign_in(bot_token=bot_token)
    result = await telegram_client.is_user_authorized()
    await telegram_client.disconnect()
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "false"
    return result


async def logout_user(client_session: ClientSession) -> str:
    """Do log-out from telegram."""
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    telegram_client = get_client(client_session=client_session)
    await telegram_client.connect()
    await telegram_client.log_out()
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "false"
    return "OK"


async def send_code_request(client_session: ClientSession, phone_number: str) -> str:
    """Send code request."""
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    client = get_client(client_session=client_session)
    await client.connect()
    try:
        result = await client.send_code_request(phone_number)
    except FloodWaitError as e:
        logger.error(str(e))
        return "try again later"
    finally:
        await client.disconnect()
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "false"
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
    async for login in Login.objects.filter(have_to_send_code=True):
        client_session = await ClientSession.objects.filter(id=login.client_session.id).afirst()
        phone_hash = await send_code_request(client_session, login.phone_number)
        login.hash_code = phone_hash
        login.have_to_send_code = False
        login.save()
    async for login in Login.objects.select_related("client_session").filter(code__isnull=False):
        login_result = None
        try:
            if login.bot_token:
                login_result = await login_bot(login.client_session, login.bot_token)
            else:
                login_result = await login_user(
                    login.client_session, login.phone_number, login.code, login.passcode, login.hash_code
                )
        except telethon.errors.rpcerrorlist.PhoneCodeExpiredError:
            login.have_to_send_code = True
            login.save()

        if login_result:
            login.client_session.login_status = LoginStatus.LOGIN_WAITING_FOR_TELEGRAM_CLIENT
            login.client_session.save()
            logger.debug(f"Login successfully for client: {login.client_session.name}")
        else:
            logger.debug(f"Login failed for client: {login.client_session.name}")
        async for client in ClientSession.objects.filter(login_status=LoginStatus.LOGIN_WAITING_FOR_TELEGRAM_CLIENT):
            await connect_client(client_session=client)


async def reconnect_client(client: str):
    # check for request code
    login = await Login.objects.filter(have_to_send_code=True, client_session__name=client).afirst()
    client_session = await ClientSession.objects.filter(name=client).afirst()
    if login:
        phone_hash = await send_code_request(client_session, login.phone_number)
        login.hash_code = phone_hash
        login.have_to_send_code = False
        await sync_to_async(login.save)()
        return
    # check for login with code
    login = await Login.objects.filter(code__isnull=False, client_session__name=client).afirst()
    if not login:
        return
    try:
        if login.bot_token:
            login_result = await login_bot(login.client_session, login.bot_token)
        else:
            login_result = await login_user(
                login.client_session, login.phone_number, login.code, login.passcode, login.hash_code
            )
    except telethon.errors.rpcerrorlist.PhoneCodeExpiredError:
        login.have_to_send_code = True
        await sync_to_async(login.save)()
        return

    if login_result:
        login.client_session.login_status = LoginStatus.LOGIN_WAITING_FOR_TELEGRAM_CLIENT
        login.client_session.save()
        logger.debug(f"Login successfully for client: {login.client_session.name}")
        await connect_client(client_session=client_session)
    else:
        logger.debug(f"Login failed for client: {login.client_session.name}")


async def normalize_results(results: ChannelMessages, chat_name: str) -> list:
    if not results:
        return []

    messages: list[dict] = []
    for message in results.messages:
        if not message.message:
            continue
        peer = message.from_id if message.from_id else message.peer_id
        if isinstance(peer, PeerChannel):
            from_id = peer.channel_id
        else:
            from_id = peer.user_id
        # storing only MAX_LENGTH_FOR_REQUEST characters
        cropped_message = message.message[:MAX_LENGTH_FOR_REQUEST]
        if message not in [di["message"] for di in messages]:
            messages.append(
                {
                    "message_date": message.date,
                    "message": cropped_message,
                    "message_id": message.id,
                    "chat_id": message.peer_id.channel_id,
                    "chat_username": chat_name,
                    "from_user_id": from_id,
                }
            )
    return messages


def get_average_results(messages: list[list]) -> list:
    """Get the average number of recent messages from each chat and put it in another list."""
    result = []
    list_count = len(messages)
    sorted_messages = sorted(messages, key=len)
    used = 0
    for num, msg in enumerate(sorted_messages):
        cnt = round((MAX_ANSWERS_PER_REQUEST - used) / (list_count - num))
        if len(msg) <= cnt:
            used += len(msg)
            result += msg
        else:
            used += cnt
            result += msg[:cnt]
    return result


async def get_search_request(client: TelegramClient, query: str, chats: list) -> list:
    await client.connect()
    results = []
    for chat in chats:
        chat_messages = await client(
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
        chat_messages = await normalize_results(results=chat_messages, chat_name=chat.username)
        results.append(chat_messages)

    client.disconnect()
    return sorted(
        get_average_results(results), key=lambda dictionary: dictionary["message_date"].timestamp(), reverse=True
    )
