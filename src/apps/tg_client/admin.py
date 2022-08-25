from asyncio import run

from apps.tg_client.helpers import login_user
from apps.tg_client.helpers import logout_user
from apps.tg_client.helpers import send_code_request
from apps.tg_client.models import ClientSession
from apps.tg_client.models import Login
from apps.tg_client.models import Session
from django.contrib import admin


def send_request_code(modeladmin, request, queryset):
    for qs in queryset:
        if not qs.have_to_send_code:
            hash_code = run(send_code_request(qs.client_session, qs.phone_number))
            qs.hash_code = hash_code
            qs.have_to_send_code = False
            qs.save()


send_request_code.short_description = "Send request code"  # type: ignore


def login(modeladmin, request, queryset):
    for qs in queryset:
        is_user_authorized = run(
            login_user(
                client_session=qs.client_session,
                phone_number=qs.phone_number,
                code=qs.code,
                password=qs.passcode,
                phone_code_hash=qs.hash_code,
            )
        )
        print(f"user authorized: {is_user_authorized}")


login.short_description = "Login"  # type: ignore


def logout(modeladmin, request, queryset):
    for qs in queryset:
        result = run(logout_user(client_session=qs.client_session))
        qs.delete()
        print(result)


logout.short_description = "Logout"  # type: ignore


class ClientSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "login_status"]
    list_filter = ("login_status",)


@admin.register(Login)
class LoginAdmin(admin.ModelAdmin):
    actions = [send_request_code, login, logout]
    list_display = [
        "id",
        "client_session",
        "have_to_send_code",
        "bot_token",
        "phone_number",
        "code",
        "passcode",
        "hash_code",
        "created_at",
    ]
    list_filter = ["created_at", "client_session__name"]


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
