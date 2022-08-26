from apps.tg_client.models import ClientSession
from apps.tg_client.sessions import DjangoSession
from config.telegram import CLIENT_SESSION_SEARCH
from config.telegram import TELEGRAM_API_HASH
from config.telegram import TELEGRAM_API_ID
from django.shortcuts import render
from django.views.generic.base import View
from telethon import TelegramClient


class index(View):
    async def get(self, request, *args, **kwargs):
        # client_session = ClientSession.objects.filter(name=CLIENT_SESSION_SEARCH).first()
        # client = TelegramClient(DjangoSession(client_session=client_session),
        #                         api_id=TELEGRAM_API_ID,
        #                         api_hash=TELEGRAM_API_HASH
        #                         )
        # await client.connect()
        # info = await client.get_me()
        info = "hello world"
        return render(request, "index.html", context={"info": info})
