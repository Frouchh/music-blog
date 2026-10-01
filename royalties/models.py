from django.db import models

from accounts.models import AuthorProfile
from orders.models import OrderItem


class Royalty(models.Model):
    author = models.ForeignKey(AuthorProfile, on_delete=models.PROTECT, related_name='royalties')
    order_item = models.OneToOneField(OrderItem, on_delete=models.PROTECT, related_name='royalty')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'royalties'
        ordering = ['-created_at']
        verbose_name = 'Начисление'
        verbose_name_plural = 'Начисления'


class Payout(models.Model):
    STATUS = [('requested', 'На рассмотрении'), ('paid', 'Выплачено'),
              ('rejected', 'Отклонено')]

    author = models.ForeignKey(AuthorProfile, on_delete=models.PROTECT, related_name='payouts')
    amount = models.DecimalField('Сумма, руб.', max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS, default='requested')
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'payouts'
        ordering = ['-requested_at']
        verbose_name = 'Выплата'
        verbose_name_plural = 'Выплаты'
