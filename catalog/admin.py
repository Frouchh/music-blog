from django.contrib import admin

from .models import Album, Genre, LicenseType, Review, Status, Track, TrackLicense


class TrackLicenseInline(admin.TabularInline):
    model = TrackLicense
    extra = 0


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'genre', 'status', 'created_at']
    list_filter = ['status', 'genre']
    search_fields = ['title', 'author__stage_name']
    inlines = [TrackLicenseInline]


admin.site.register([Genre, Status, Album, LicenseType, Review])
