import os
from asyncio import run

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.bot")
django.setup()


if __name__ == "__main__":
    from apps.bot import dispatcher

    dispatcher.run_pooling()
