from django.shortcuts import render
from django.views.generic.base import View


class index(View):
    async def get(self, request, *args, **kwargs):
        info = "hello world"
        return render(request, "index.html", context={"info": info})
