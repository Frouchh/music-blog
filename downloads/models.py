from django.db import models
from django.utils import timezone

from orders.models import OrderItem


class DownloadLink(models.Model):
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE,
                                      related_name='download_link')
    token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    downloads_count = models.PositiveIntegerField(default=0)
    max_downloads = models.PositiveIntegerField(default=3)

    class Meta:
        db_table = 'download_links'
        verbose_name = 'Ссылка на скачивание'
        verbose_name_plural = 'Ссылки на скачивание'

    @property
    def is_active(self):
        return self.expires_at > timezone.now() and self.downloads_count < self.max_downloads

    @property
    def downloads_left(self):
        return max(self.max_downloads - self.downloads_count, 0)
