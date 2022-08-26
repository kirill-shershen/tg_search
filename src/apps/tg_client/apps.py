from config.logger import logger
from config.telegram import CLIENT_SESSION_BOT
from config.telegram import CLIENT_SESSION_SEARCH
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def init_default_sessions(sender, **kwargs):
    from apps.tg_client.models import ClientSession, Login

    search, created = ClientSession.objects.get_or_create(name=CLIENT_SESSION_SEARCH)
    if created:
        logger.info("search session created")
    bot, _ = ClientSession.objects.get_or_create(name=CLIENT_SESSION_BOT)
    if created:
        logger.info("bot session created")
    _, created = Login.objects.get_or_create(client_session=search)
    if created:
        logger.info("search login created")
    _, created = Login.objects.get_or_create(client_session=bot)
    if created:
        logger.info("bot login created")


class TgClientConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tg_client"

    def ready(self):
        post_migrate.connect(init_default_sessions, sender=self)
