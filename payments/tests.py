from types import SimpleNamespace
from unittest import mock

from django.test import override_settings
from django.urls import reverse

from audio_shop.test_utils import ShopTestCase
from orders.models import Order


@override_settings(YOOKASSA_SHOP_ID='123456', YOOKASSA_SECRET_KEY='test_key')
class YooKassaTests(ShopTestCase):
    """Режим с ключами ЮKassa: SDK подменяется, проверяются перенаправление и возврат."""

    def fake_payment(self, status='pending'):
        return SimpleNamespace(id='2d8f-test', status=status, confirmation=SimpleNamespace(
            confirmation_url='https://yoomoney.ru/checkout/payments/v2/contract?orderId=2d8f-test'))

    def test_checkout_redirects_to_yookassa(self):
        self.client.force_login(self.buyer)
        self.client.post(reverse('cart_add'), {'license_id': self.licenses['Личная'].pk})
        with mock.patch('yookassa.Payment.create', return_value=self.fake_payment()) as create:
            response = self.client.post(reverse('checkout'), {'agree': 'on'})
        self.assertRedirects(response, self.fake_payment().confirmation.confirmation_url,
                             fetch_redirect_response=False)
        params = create.call_args[0][0]
        self.assertEqual(params['amount'], {'value': '149.00', 'currency': 'RUB'})
        self.assertIn('/payments/result/', params['confirmation']['return_url'])

    def test_return_from_yookassa_completes_order(self):
        self.test_checkout_redirects_to_yookassa()
        order = Order.objects.get()
        with mock.patch('yookassa.Payment.find_one', return_value=self.fake_payment('succeeded')):
            response = self.client.get(reverse('payment_result', args=[order.pk]))
        self.assertContains(response, 'Оплата прошла успешно')
        order.refresh_from_db()
        self.assertEqual(order.status, 'paid')
