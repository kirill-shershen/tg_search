import os

USER_PROFILE = "tg://user?id="

TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY", None)
TELEGRAM_API_ID = os.environ.get("TELEGRAM_API_ID", None)
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH", None)

CLIENT_SESSION_SEARCH = os.environ.get("CLIENT_SESSION_SEARCH", "search")
CLIENT_SESSION_BOT = os.environ.get("CLIENT_SESSION_BOT", "bot")

BOT_RECONNECT_TIMER_MIN = int(os.environ.get("BOT_RECONNECT_TIMER_MIN", 1)) * 60
