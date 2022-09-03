import os

from .base import *  # type: ignore

DEBUG = os.getenv("DEBUG", True)

ALLOW_HOST = os.environ.get("ALLOW_HOST", "0.0.0.0")

ALLOWED_HOSTS = [
    ALLOW_HOST,
    f"www.{ALLOW_HOST}",
    "127.0.0.1",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "postgres"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "postgres"),
        "HOST": os.environ.get("DB_HOST", "db"),
        "PORT": os.environ.get("DB_PORT", 5432),
    }
}
