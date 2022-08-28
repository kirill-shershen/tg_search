from config.telegram import USER_PROFILE
from core.models import GetOrNoneManager
from core.models import TimeStampedModel
from django.db import models
from django.db.models import Index
from versatileimagefield.fields import VersatileImageField


class User(TimeStampedModel):
    user_id = models.IntegerField(null=False, unique=True, help_text="telegram user id")
    username = models.CharField(max_length=150, null=True, blank=True, help_text="telegram user name")
    first_name = models.CharField(max_length=30, null=True, blank=True, help_text="telegram user first name")
    last_name = models.CharField(max_length=30, null=True, blank=True, help_text="telegram user last name")
    phone = models.CharField(max_length=20, null=True, blank=True, help_text="telegram user phone")
    photo = VersatileImageField(null=True, blank=True, upload_to="images", help_text="telegram first photo")

    Index(fields=["user_id"], name="telegram_user_id_idx")

    def __str__(self):
        return f"PK {self.id} TG:{self.username}"

    @property
    def name(self):
        return str(self.first_name if self.first_name else self.username)


class UserChat(TimeStampedModel):
    user = models.ForeignKey("bot.User", on_delete=models.CASCADE, null=True, related_name="chats")
    username = models.CharField(max_length=40, null=False, default="", help_text="telegram chat username")
    title = models.CharField(max_length=255, null=False, default="", help_text="telegram chat title")
    chat_id = models.PositiveIntegerField(null=False, default=0, help_text="telegram chat id")

    objects = GetOrNoneManager()

    class Meta:
        verbose_name = "User Chat"
        verbose_name_plural = "User Chat"


class SearchQuery(TimeStampedModel):
    user = models.ForeignKey("bot.User", on_delete=models.CASCADE, null=True, related_name="queries")
    chat = models.ForeignKey("bot.UserChat", on_delete=models.CASCADE, null=True, related_name="queries")
    query = models.CharField(max_length=100, null=False, help_text="query string")

    class Meta:
        verbose_name = "Search Query"
        verbose_name_plural = "Search Query"


class QueryResult(TimeStampedModel):
    query = models.ForeignKey("bot.SearchQuery", on_delete=models.CASCADE, null=True, related_name="results")
    message = models.CharField(max_length=100, null=False, help_text="query result")
    message_date = models.DateField(blank=True, null=True, help_text="telegram message date")
    from_user_id = models.IntegerField(null=False, help_text="message author id")
    from_user_name = models.CharField(max_length=100, null=False, help_text="message author name")

    @property
    def user_profile_link(self):
        return f"({self.from_user_name})[{USER_PROFILE}{self.from_user_id}]"

    class Meta:
        verbose_name = "Query Result"
        verbose_name_plural = "Query Result"


class ChatText(TimeStampedModel):
    name = models.CharField(max_length=200, null=False, blank=False, help_text="name of text")
    text = models.TextField(help_text="text for chat")

    class Meta:
        verbose_name = "Chat text"
        verbose_name_plural = "Chat text"

    def __str__(self):
        return f"{self.name}"
