# Generated by Django 4.1 on 2022-08-25 08:41
import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    initial = True

    dependencies: list = []

    operations = [
        migrations.CreateModel(
            name="ClientSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Client Session Name")),
                (
                    "login_status",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "Login Required"),
                            (2, "Login Done"),
                            (3, "Login Failed"),
                            (4, "Login Waiting For Telegram Client"),
                        ],
                        default=1,
                        verbose_name="Login Required",
                    ),
                ),
            ],
            options={
                "verbose_name": "Client Session",
                "verbose_name_plural": "Client Sessions",
            },
        ),
        migrations.CreateModel(
            name="Login",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("have_to_send_code", models.BooleanField(default=True, verbose_name="Have to send code")),
                ("bot_token", models.CharField(blank=True, max_length=255, null=True, verbose_name="Bot token")),
                ("phone_number", models.CharField(blank=True, max_length=20, null=True, verbose_name="Phone number")),
                ("code", models.CharField(blank=True, max_length=10, null=True, verbose_name="Code")),
                ("passcode", models.CharField(blank=True, max_length=100, null=True, verbose_name="Passcode")),
                ("hash_code", models.CharField(blank=True, max_length=100, null=True, verbose_name="Hash code")),
                (
                    "client_session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tg_client.clientsession",
                        verbose_name="Client session",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at", "-updated_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Session",
            fields=[
                (
                    "client_session",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="tg_client.clientsession",
                        verbose_name="Client Session",
                    ),
                ),
                ("auth_key", models.BinaryField(editable=True, verbose_name="Auth Key")),
                ("data_center_id", models.IntegerField(db_index=True, verbose_name="Data Center ID")),
                ("port", models.IntegerField(verbose_name="Port")),
                ("server_address", models.CharField(max_length=255, verbose_name="Server Address")),
                ("takeout_id", models.BigIntegerField(null=True, verbose_name="Takeout ID")),
            ],
            options={
                "verbose_name": "Session",
                "verbose_name_plural": "Sessions",
                "unique_together": {("client_session_id", "data_center_id")},
            },
        ),
    ]
