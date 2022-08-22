from core.models import TimeStampedModel
from django.contrib.auth.models import AbstractUser
from django.db import models
from versatileimagefield.fields import VersatileImageField


class User(AbstractUser, TimeStampedModel):
    username = models.CharField(max_length=150, unique=True, null=True, blank=True, help_text="telegram user name")
    telegram_user_id = models.IntegerField(null=False, default=0, help_text="telegram user id")
    photo = VersatileImageField(null=True, blank=True, upload_to="images", help_text="telegram first photo")

    def __str__(self):
        return f"PK {self.id} TG:{self.username} EMAIL:{self.email}"


class UserChat(TimeStampedModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, related_name="users")
    name = models.CharField(max_length=150, null=False, default="", help_text="telegram chat name")

    class Meta:
        verbose_name = "User Chat"
        verbose_name_plural = "User Chat"
