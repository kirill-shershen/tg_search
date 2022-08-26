import os
from asyncio import run

import django
from apps.bot.dispatcher import run_pooling

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.bot")
django.setup()


if __name__ == "__main__":
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    run(run_pooling())
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "false"
