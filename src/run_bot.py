import os
from asyncio import run

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.bot")
django.setup()


if __name__ == "__main__":
    from apps.bot import dispatcher

    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
    dispatcher.run_pooling()
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "false"
