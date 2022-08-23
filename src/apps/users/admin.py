from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserChat

UserAdmin.list_display = ("photo",) + UserAdmin.list_display
UserAdmin.fieldsets += (
    ('telegram', {
        'fields': (
            "photo",
            "telegram_user_id"
        )
    }),
)

admin.site.register(User, UserAdmin)
admin.site.register(UserChat, admin.ModelAdmin)