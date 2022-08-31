from pathlib import Path

from django.apps import apps


def get_fixture(name: str, app: str):
    conf = apps.get_app_config(app)
    return Path(conf.path, f"fixtures/{name}")
