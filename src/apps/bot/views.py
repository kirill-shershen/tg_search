from django.shortcuts import render
from django.views.generic.base import View


class index(View):
    async def get(self, request, *args, **kwargs):

        # info = await telegram_client.get_me()).stringify()
        # Apps
        info = ""
        return render(request, "index.html", context={"info": info})
