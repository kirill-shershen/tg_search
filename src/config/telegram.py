import os

MESSAGE_DEEP_LINK = "tg://openmessage?chat_id={chat_id}&message_id={message_id}"
MESSAGE_LINK = "https://t.me/{chat_id}/{message_id}"

TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY", None)
TELEGRAM_API_ID = os.environ.get("TELEGRAM_API_ID", None)
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH", None)

CLIENT_SESSION_SEARCH = os.environ.get("CLIENT_SESSION_SEARCH", "search")
CLIENT_SESSION_BOT = os.environ.get("CLIENT_SESSION_BOT", "bot")

BOT_RECONNECT_TIMER_MIN = int(os.environ.get("BOT_RECONNECT_TIMER_MIN", default=1)) * 60
MAX_GROUPS_PER_USER = int(os.environ.get("MAX_GROUPS_PER_USER", default=5))
MAX_ANSWERS_PER_REQUEST = int(os.environ.get("MAX_ANSWERS_PER_REQUEST", default=40))
MAX_REQUESTS_PER_DAY = int(os.environ.get("MAX_REQUESTS_PER_DAY", default=20))
MAX_LENGTH_FOR_REQUEST = int(os.environ.get("MAX_LENGTH_FOR_REQUEST", default=100))
MAX_LENGTH_FOR_MESSAGE = int(os.environ.get("MAX_LENGTH_FOR_MESSAGE", default=3600))
CHAT_TEXT_START = os.environ.get("CHAT_TEXT_START", "start")
CHAT_TEXT_ADD_CHAT = os.environ.get("CHAT_TEXT_ADD_CHAT", "➕ чат")
CHAT_TEXT_WRONG_CHAT = os.environ.get("CHAT_TEXT_WRONG_CHAT", "wrong")
CHAT_TEXT_EXIST_CHAT = os.environ.get("CHAT_TEXT_EXIST_CHAT", "exist")
CHAT_TEXT_NOWHERE_SEARCH = os.environ.get("CHAT_TEXT_NOWHERE_SEARCH", "nowhere_search")
CHAT_TEXT_DAILY_LIMIT = os.environ.get("CHAT_TEXT_DAILY_LIMIT", "daily_limit")
CHAT_TEXT_ADD_CHAT_REJECT_MAX = os.environ.get("CHAT_TEXT_ADD_CHAT_REJECT_MAX", "max chat per user")
CHAT_TEXT_SEARCH = os.environ.get("CHAT_TEXT_SEARCH", "🔍 поиск")
CHAT_TEXT_SEARCH_RESULT = os.environ.get("CHAT_TEXT_SEARCH_RESULT", "result")
CHAT_TEXT_SUCCESS = os.environ.get("CHAT_TEXT_SUCCESS", "success")
CHAT_TEXT_FAILED = os.environ.get("CHAT_TEXT_FAILED", "failed")
CHAT_TEXT_GROUP_LIST = os.environ.get("CHAT_TEXT_GROUP_LIST", "group_list")
