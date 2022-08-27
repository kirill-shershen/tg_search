from apps.bot.models import ChatText
from apps.bot.models import QueryResult
from apps.bot.models import SearchQuery
from apps.bot.models import User
from apps.bot.models import UserChat
from django.contrib import admin

admin.site.register(SearchQuery, admin.ModelAdmin)
admin.site.register(QueryResult, admin.ModelAdmin)
admin.site.register(User, admin.ModelAdmin)


@admin.register(UserChat)
class UserChatAdmin(admin.ModelAdmin):
    list_display = ["user", "chat_id", "username", "title"]
    ordering = ("user", "title")


@admin.register(ChatText)
class ChatTextAdmin(admin.ModelAdmin):
    list_display = ["name", "text"]
    fieldsets = (
        (
            "Content",
            {"fields": ("name", "text")},
        ),
    )
