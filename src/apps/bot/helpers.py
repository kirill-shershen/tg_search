import datetime
from itertools import count
from typing import Optional

from apps.bot.models import ChatText
from config.telegram import CHAT_TEXT_ADD_CHAT
from config.telegram import CHAT_TEXT_ADD_CHAT_REJECT_MAX
from config.telegram import CHAT_TEXT_DELETE_CHAT
from config.telegram import CHAT_TEXT_SEARCH
from config.telegram import CHAT_TEXT_SEARCH_RESULT
from config.telegram import CHAT_TEXT_START
from config.telegram import MAX_GROUPS_PER_USER
from config.telegram import MESSAGE_LINK


def get_start_message(name: Optional[str]) -> str:
    if name:
        return ChatText.objects.get(name=CHAT_TEXT_START).text % name
    else:
        return ChatText.objects.get(name=CHAT_TEXT_START).text


def get_add_chat_message(chat_list: list) -> str:
    return ChatText.objects.get(name=CHAT_TEXT_ADD_CHAT).text.format(
        count=MAX_GROUPS_PER_USER, chats="\n".join(f"{num} {chat.title}" for num, chat in enumerate(chat_list, 1))
    )


def get_delete_chat_message() -> str:
    return ChatText.objects.get(name=CHAT_TEXT_DELETE_CHAT).text


def get_add_chat_reject_max() -> str:
    return ChatText.objects.get(name=CHAT_TEXT_ADD_CHAT_REJECT_MAX).text


def get_search_message(chat_list: list, request_count: int) -> str:
    return ChatText.objects.get(name=CHAT_TEXT_SEARCH).text.format(
        request_count=request_count, chats="\n".join(f"{num} {chat.title}" for num, chat in enumerate(chat_list, 1))
    )


def get_message_link(date: datetime.datetime, chat_name: str, message_id: int) -> str:
    # return f"[{date:%Y-%m-%d %H:%M}]({MESSAGE_LINK.format(chat_id=chat_id, message_id=message_id)})"
    # <a href=tg://user?id={me.id}>{me.first_name}
    return f"<a href={MESSAGE_LINK.format(chat_id=chat_name, message_id=message_id)}>{date:%Y-%m-%d %H:%M}</a>"


def get_result_message(messages: list, query: str) -> str:
    text_messages = ""
    for num, mesg in enumerate(messages, 1):
        date_deep_link = get_message_link(
            date=mesg["message_date"], chat_name=mesg["chat_username"], message_id=mesg["message_id"]
        )
        text_messages += f"{date_deep_link} {mesg['message'][:100].strip()}\n\n"

    return ChatText.objects.get(name=CHAT_TEXT_SEARCH_RESULT).text.format(query=query, messages=text_messages)
