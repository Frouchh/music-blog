from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AuthorProfile, Role, User


@admin.register(User)
class ShopUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_blocked', 'date_joined']
    list_filter = ['role', 'is_blocked']
    fieldsets = UserAdmin.fieldsets + (('Магазин', {'fields': ('role', 'is_blocked')}),)


admin.site.register(Role)
admin.site.register(AuthorProfile)
