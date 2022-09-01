import asyncio
from asyncio import run

from apps.tg_client.helpers import login_bot
from apps.tg_client.helpers import login_user
from apps.tg_client.helpers import logout_user
from apps.tg_client.helpers import send_code_request
from apps.tg_client.models import ClientSession
from apps.tg_client.models import Login
from apps.tg_client.models import LoginStatus
from apps.tg_client.models import Session
from asgiref.sync import async_to_sync
from config.logger import logger
from django.contrib import admin


async def stop():
    await asyncio.sleep(3)


@admin.action(description="Send request code")
def send_request_code(modeladmin, request, queryset):
    """Send requests and receive hash codes for all selected Logins"""
    for qs in queryset:
        if qs.have_to_send_code:
            hash_code = run(send_code_request(client_session=qs.client_session, phone_number=qs.phone_number))
            qs.hash_code = hash_code
            qs.have_to_send_code = False
            qs.save()


@admin.action(description="Login")
def login(modeladmin, request, queryset):
    """Send requests and receive hash codes for all selected Logins"""
    for qs in queryset:
        if qs.bot_token:
            is_user_authorized = async_to_sync(login_bot)(client_session=qs.client_session, bot_token=qs.bot_token)
            logger.debug(f"{qs.bot_token} authorized {is_user_authorized}")
        elif all([qs.code, qs.phone_number, qs.hash_code]):
            is_user_authorized = run(
                login_user(
                    client_session=qs.client_session,
                    phone_number=qs.phone_number,
                    code=qs.code,
                    password=qs.passcode,
                    phone_code_hash=qs.hash_code,
                )
            )
            logger.debug(f"{qs.phone_number} authorized {is_user_authorized}")
        if is_user_authorized:
            qs.client_session.login_status = LoginStatus.LOGIN_WAITING_FOR_TELEGRAM_CLIENT
            qs.client_session.save()


@admin.action(description="Logout")
def logout(modeladmin, request, queryset):
    """Log-out all selected Logins"""
    for qs in queryset:
        result = run(logout_user(client_session=qs.client_session))
        qs.code = ""
        qs.hash_code = ""
        qs.client_session.login_status = LoginStatus.LOGIN_REQUIRED
        qs.save()
        print(result)


class ClientSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "login_status"]
    list_filter = ("login_status",)


@admin.register(Login)
class LoginAdmin(admin.ModelAdmin):
    actions = [send_request_code, login, logout]
    list_display = [
        "client_session",
        "have_to_send_code",
        "bot_token",
        "phone_number",
        "code",
        "passcode",
        "hash_code",
    ]
    list_filter = ["client_session__name"]


class SessionAdmin(admin.ModelAdmin):
    list_display = [
        "client_session",
        "auth_key",
        "data_center_id",
        "port",
        "server_address",
        "takeout_id",
    ]
    raw_id_fields = ["client_session"]
    list_filter = ["client_session__name"]


admin.site.register(Session, SessionAdmin)
admin.site.register(ClientSession, ClientSessionAdmin)
