from django.contrib import admin

from .models import DownloadLink


@admin.register(DownloadLink)
class DownloadLinkAdmin(admin.ModelAdmin):
    list_display = ['order_item', 'expires_at', 'downloads_count', 'max_downloads']
