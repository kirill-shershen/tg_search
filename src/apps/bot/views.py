import os

from django.shortcuts import render
from django.views.generic.base import View


class index(View):
    async def get(self, request, *args, **kwargs):
        info = os.getenv("DJANGO_SETTINGS_MODULE")
        return render(request, "index.html", context={"info": info})
