from django.contrib import admin

from .models import PaymentLog


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ['external_id', 'order', 'amount', 'status', 'created_at']
    list_filter = ['status']
    readonly_fields = ['order', 'external_id', 'amount', 'status', 'created_at', 'updated_at']
