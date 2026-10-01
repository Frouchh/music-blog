from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from audio_shop.test_utils import ShopTestCase
from orders.models import Order, OrderItem
from orders.services import complete_order

from .models import DownloadLink


class DownloadTests(ShopTestCase):
    def setUp(self):
        order = Order.objects.create(buyer=self.buyer, total=149, status='pending')
        OrderItem.objects.create(order=order, track_license=self.licenses['Личная'], price=149)
        complete_order(order)
        self.link = DownloadLink.objects.get()
        self.url = reverse('download', args=[self.link.token])

    def test_download_limit(self):
        self.client.force_login(self.buyer)
        for _ in range(3):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            b''.join(response.streaming_content)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_foreign_link_is_forbidden(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_expired_link(self):
        DownloadLink.objects.update(expires_at=timezone.now() - timedelta(minutes=1))
        self.client.force_login(self.buyer)
        self.assertEqual(self.client.get(self.url).status_code, 410)

    def test_full_file_has_no_public_url(self):
        with self.assertRaises(ValueError):
            self.track.audio_file.url
