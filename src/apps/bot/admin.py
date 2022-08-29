from apps.bot.models import ChatText
from apps.bot.models import QueryResult
from apps.bot.models import SearchQuery
from apps.bot.models import User
from apps.bot.models import UserChat
from django.contrib import admin

admin.site.register(User, admin.ModelAdmin)


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "query"]
    ordering = ("-created_at",)


@admin.register(QueryResult)
class QueryResultAdmin(admin.ModelAdmin):
    list_display = ["query", "message", "message_date"]
    ordering = ("query", "-message_date")


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
