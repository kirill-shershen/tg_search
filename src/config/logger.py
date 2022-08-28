import logging

from django.conf import settings

loglevel = logging.DEBUG if settings.DEBUG else logging.INFO
logging.basicConfig(format="%(levelname)s:%(message)s", level=loglevel)
logger = logging.getLogger("BotLogger")
logger.setLevel(loglevel)
