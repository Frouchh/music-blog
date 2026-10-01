from django.conf import settings
from django.db import models

from catalog.models import TrackLicense


class Order(models.Model):
    STATUS = [('new', 'Создан'), ('pending', 'Ожидает оплаты'),
              ('paid', 'Оплачен'), ('canceled', 'Отменён')]

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                              related_name='orders')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ №{self.pk}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    track_license = models.ForeignKey(TrackLicense, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # цена на момент покупки

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return str(self.track_license)
