import os

USER_PROFILE = "tg://user?id="

TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY", None)
TELEGRAM_API_ID = os.environ.get("TELEGRAM_API_ID", None)
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH", None)

CLIENT_SESSION_SEARCH = os.environ.get("CLIENT_SESSION_SEARCH", "search")
CLIENT_SESSION_BOT = os.environ.get("CLIENT_SESSION_BOT", "bot")

BOT_RECONNECT_TIMER_MIN = int(os.environ.get("BOT_RECONNECT_TIMER_MIN", 1)) * 60
MAX_GROUPS_PER_USER = int(os.environ.get("MAX_GROUPS_PER_USER", 5))
MAX_ANSWERS_PER_REQUEST = int(os.environ.get("MAX_ANSWERS_PER_REQUEST", 40))
MAX_REQUESTS_PER_DAY = int(os.environ.get("MAX_REQUESTS_PER_DAY", 20))

CHAT_TEXT_START = os.environ.get("CHAT_TEXT_START", "start")
CHAT_TEXT_ADD_CHAT = os.environ.get("CHAT_TEXT_ADD_CHAT", "➕ чат")
CHAT_TEXT_ADD_CHAT_REJECT_MAX = os.environ.get("CHAT_TEXT_ADD_CHAT_REJECT_MAX", "max chat per user")
CHAT_TEXT_DELETE_CHAT = os.environ.get("CHAT_TEXT_DELETE_CHAT", "➖ чат")
