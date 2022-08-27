from core.models import TimeStampedModel
from django.db import models


class Login(models.Model):
    client_session = models.OneToOneField(
        "ClientSession",
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name="Client Session",
    )
    have_to_send_code = models.BooleanField(default=True, verbose_name="Have to send code")
    bot_token = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Bot token",
    )
    phone_number = models.CharField(
        max_length=20,
        null=False,
        verbose_name="Phone number",
    )
    code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="Code",
    )
    passcode = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Passcode",
    )
    hash_code = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Hash code",
    )

    def __str__(self):
        return f"{self.client_session}"


class LoginStatus(models.IntegerChoices):
    LOGIN_REQUIRED = 1
    LOGIN_DONE = 2
    LOGIN_FAILED = 3
    LOGIN_WAITING_FOR_TELEGRAM_CLIENT = 4

    @classmethod
    def approve(cls) -> list:
        return [cls.LOGIN_DONE, cls.LOGIN_WAITING_FOR_TELEGRAM_CLIENT]


class ClientSession(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Client Session Name",
    )
    login_status = models.PositiveSmallIntegerField(
        default=LoginStatus.LOGIN_REQUIRED,
        choices=LoginStatus.choices,
        verbose_name="Login Required",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Client Session"
        verbose_name_plural = "Client Sessions"


class Session(models.Model):
    client_session = models.OneToOneField(
        "ClientSession",
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name="Client Session",
    )
    auth_key = models.BinaryField(
        blank=False,
        null=False,
        editable=True,
        verbose_name="Auth Key",
    )
    data_center_id = models.IntegerField(
        db_index=True,
        verbose_name="Data Center ID",
    )
    port = models.IntegerField(
        verbose_name="Port",
    )
    server_address = models.CharField(
        max_length=255,
        verbose_name="Server Address",
    )
    takeout_id = models.BigIntegerField(
        null=True,
        verbose_name="Takeout ID",
    )

    class Meta:
        unique_together = (
            (
                "client_session_id",
                "data_center_id",
            ),
        )
        verbose_name = "Session"
        verbose_name_plural = "Sessions"

    def __str__(self):
        return f"{self.client_session}"
