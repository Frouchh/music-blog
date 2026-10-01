from django.db import models

from orders.models import Order


class PaymentLog(models.Model):
    """Журнал платёжных операций (логирование финансовых операций по ТЗ)."""
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='payments')
    external_id = models.CharField('Идентификатор платежа в ЮKassa', max_length=64, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        verbose_name = 'Платёж'
        verbose_name_plural = 'Журнал платежей'

    def __str__(self):
        return f'{self.external_id} ({self.status})'
