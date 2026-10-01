from decimal import Decimal

from django.urls import reverse

from accounts.models import AuthorProfile
from audio_shop.test_utils import ShopTestCase
from catalog.models import TrackLicense
from downloads.models import DownloadLink
from payments.models import PaymentLog
from royalties.models import Royalty

from .models import Order
from .services import author_reward


class PurchaseTests(ShopTestCase):
    def buy(self, license_name, result='pay'):
        """Полный сценарий: корзина → оформление → тестовая оплата."""
        self.client.force_login(self.buyer)
        self.client.post(reverse('cart_add'), {'license_id': self.licenses[license_name].pk})
        response = self.client.post(reverse('checkout'))
        log = PaymentLog.objects.latest('created_at')
        self.assertRedirects(response, reverse('test_payment', args=[log.external_id]))
        self.client.post(reverse('test_payment', args=[log.external_id]), {'result': result})
        return Order.objects.get(pk=log.order_id), log

    def test_reward_formula(self):
        self.assertEqual(author_reward(Decimal('990')), Decimal('891.00'))
        self.assertEqual(author_reward(Decimal('149')), Decimal('134.10'))

    def test_successful_payment(self):
        order, _ = self.buy('Коммерческая')
        self.assertEqual(order.status, 'paid')
        self.assertEqual(DownloadLink.objects.filter(order_item__order=order).count(), 1)
        self.author.refresh_from_db()
        self.assertEqual(self.author.balance, Decimal('891.00'))

    def test_declined_payment(self):
        order, _ = self.buy('Личная', result='decline')
        self.assertEqual(order.status, 'pending')
        self.assertFalse(DownloadLink.objects.exists())
        self.assertFalse(Royalty.objects.exists())

    def test_repeated_notification_does_not_duplicate_royalty(self):
        from payments.services import process_payment
        order, log = self.buy('Коммерческая')
        process_payment(log.external_id, 'succeeded')   # повторное уведомление
        self.assertEqual(Royalty.objects.count(), 1)
        self.assertEqual(AuthorProfile.objects.get(pk=self.author.pk).balance, Decimal('891.00'))

    def test_exclusive_license_withdraws_track(self):
        self.buy('Эксклюзивная')
        self.assertFalse(TrackLicense.objects.filter(track=self.track, is_available=True).exists())
        response = self.client.post(reverse('cart_add'),
                                    {'license_id': self.licenses['Личная'].pk})
        self.assertEqual(response.status_code, 404)

    def test_price_is_fixed_at_purchase(self):
        order, _ = self.buy('Личная')
        TrackLicense.objects.filter(pk=self.licenses['Личная'].pk).update(price=500)
        self.assertEqual(order.items.get().price, Decimal('149'))

    def test_empty_cart_checkout(self):
        self.client.force_login(self.buyer)
        response = self.client.post(reverse('checkout'))
        self.assertRedirects(response, reverse('cart'))
        self.assertFalse(Order.objects.exists())
