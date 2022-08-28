import os

import base

DEBUG = os.getenv("DEBUG", True)

SECRET_KEY = os.getenv("SECRET_KEY_BOT", "123")

INSTALLED_APPS = base.LOCAL_APPS
