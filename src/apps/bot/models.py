from config.telegram import USER_PROFILE
from core.models import TimeStampedModel
from django.db import models


class SearchQuery(TimeStampedModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, related_name="queries")
    chat = models.ForeignKey("users.UserChat", on_delete=models.CASCADE, null=True, related_name="queries")
    query = models.CharField(max_length=100, null=False, help_text="query string")

    class Meta:
        verbose_name = "Search Query"
        verbose_name_plural = "Search Query"


class QueryResult(TimeStampedModel):
    query = models.ForeignKey("bot.SearchQuery", on_delete=models.CASCADE, null=True, related_name="queries")
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
