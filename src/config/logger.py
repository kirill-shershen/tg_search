import logging
import os

loglevel = logging.DEBUG if os.getenv("DEBUG") else logging.INFO
logging.basicConfig(format="%(levelname)s:%(message)s", level=loglevel)
logger = logging.getLogger("BotLogger")
logger.setLevel(loglevel)
