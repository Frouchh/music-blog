from django.contrib import admin

from .models import Payout, Royalty


@admin.register(Royalty)
class RoyaltyAdmin(admin.ModelAdmin):
    list_display = ['author', 'order_item', 'amount', 'created_at']


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ['author', 'amount', 'status', 'requested_at', 'processed_at']
    list_filter = ['status']
