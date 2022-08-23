from django.contrib import admin

from apps.bot.models import SearchQuery, QueryResult

admin.site.register(SearchQuery, admin.ModelAdmin)
admin.site.register(QueryResult, admin.ModelAdmin)