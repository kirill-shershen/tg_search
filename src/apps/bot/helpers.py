import datetime
from typing import Optional

from apps.bot.models import ChatText
from asgiref.sync import sync_to_async
from config.telegram import CHAT_TEXT_ADD_CHAT
from config.telegram import CHAT_TEXT_ADD_CHAT_REJECT_MAX
from config.telegram import CHAT_TEXT_DAILY_LIMIT
from config.telegram import CHAT_TEXT_EXIST_CHAT
from config.telegram import CHAT_TEXT_FAILED
from config.telegram import CHAT_TEXT_GROUP_LIST
from config.telegram import CHAT_TEXT_NOWHERE_SEARCH
from config.telegram import CHAT_TEXT_SEARCH
from config.telegram import CHAT_TEXT_SEARCH_RESULT
from config.telegram import CHAT_TEXT_START
from config.telegram import CHAT_TEXT_SUCCESS
from config.telegram import CHAT_TEXT_WRONG_CHAT
from config.telegram import MAX_GROUPS_PER_USER
from config.telegram import MAX_LENGTH_FOR_MESSAGE
from config.telegram import MESSAGE_LINK


@sync_to_async
def get_help_message(name: Optional[str]) -> str:
    if name:
        return ChatText.objects.get(name=CHAT_TEXT_START).text % name
    else:
        return ChatText.objects.get(name=CHAT_TEXT_START).text


@sync_to_async
def get_success_message(success: bool = False) -> str:
    if success:
        return ChatText.objects.get(name=CHAT_TEXT_SUCCESS).text
    else:
        return ChatText.objects.get(name=CHAT_TEXT_FAILED).text


@sync_to_async
def get_add_chat_message(chat_list: list) -> str:
    return ChatText.objects.get(name=CHAT_TEXT_ADD_CHAT).text.format(
        count=MAX_GROUPS_PER_USER, chats="\n".join(f"{num} {chat.title}" for num, chat in enumerate(chat_list, 1))
    )


@sync_to_async
def get_wrong_chat_message() -> str:
    return ChatText.objects.get(name=CHAT_TEXT_WRONG_CHAT).text


@sync_to_async
def get_exist_chat_message(chat: str) -> str:
    return ChatText.objects.get(name=CHAT_TEXT_EXIST_CHAT).text.format(chat=chat)


@sync_to_async
def get_group_list_message() -> str:
    return ChatText.objects.get(name=CHAT_TEXT_GROUP_LIST).text.format(count=MAX_GROUPS_PER_USER)


@sync_to_async
def get_nowhere_search_message() -> str:
    return ChatText.objects.get(name=CHAT_TEXT_NOWHERE_SEARCH).text


@sync_to_async
def get_daily_limit_message() -> str:
    return ChatText.objects.get(name=CHAT_TEXT_DAILY_LIMIT).text


@sync_to_async
def get_add_chat_reject_max() -> str:
    return ChatText.objects.get(name=CHAT_TEXT_ADD_CHAT_REJECT_MAX).text


@sync_to_async
def get_search_message(chat_list: list, request_count: int) -> str:
    return ChatText.objects.get(name=CHAT_TEXT_SEARCH).text.format(
        request_count=request_count, chats="\n".join(f"{num} {chat.title}" for num, chat in enumerate(chat_list, 1))
    )


def get_message_link(date: datetime.datetime, chat_name: str, message_id: int) -> str:
    return f"<a href={MESSAGE_LINK.format(chat_id=chat_name, message_id=message_id)}>{date:%Y-%m-%d %H:%M}</a>"


@sync_to_async
def get_result_message(messages: list, query: str, requests_per_day_left: int) -> str:
    text_messages = ""
    for message in messages:
        date_deep_link = get_message_link(
            date=message["message_date"], chat_name=message["chat_username"], message_id=message["message_id"]
        )
        text_messages += f"{date_deep_link} {message['message'][:100].strip()}\n\n"

    return ChatText.objects.get(name=CHAT_TEXT_SEARCH_RESULT).text.format(
        query=query, messages=text_messages[:MAX_LENGTH_FOR_MESSAGE], count=requests_per_day_left
    )
