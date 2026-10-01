"""Обёртка над платёжным шлюзом.

Если в .env заданы YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY, используется
тестовый магазин ЮKassa через официальный SDK. Иначе включается встроенная
тестовая форма оплаты, чтобы весь цикл покупки можно было проверить локально.
"""
import uuid
from dataclasses import dataclass

from django.conf import settings
from django.urls import reverse


@dataclass
class GatewayPayment:
    id: str
    status: str
    confirmation_url: str = ''


def is_test_mode():
    return not (settings.YOOKASSA_SHOP_ID and settings.YOOKASSA_SECRET_KEY)


def _sdk():
    from yookassa import Configuration, Payment
    Configuration.configure(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)
    return Payment


def create_payment(order, return_url):
    if is_test_mode():
        payment_id = f'test-{uuid.uuid4()}'
        return GatewayPayment(payment_id, 'pending',
                              reverse('test_payment', args=[payment_id]))
    payment = _sdk().create({
        'amount': {'value': str(order.total), 'currency': 'RUB'},
        'confirmation': {'type': 'redirect', 'return_url': return_url},
        'capture': True,
        'description': f'Заказ №{order.id}',
        'metadata': {'order_id': order.id},
    }, str(uuid.uuid4()))                       # ключ идемпотентности
    return GatewayPayment(payment.id, payment.status,
                          payment.confirmation.confirmation_url)


def find_payment(payment_id):
    """Повторный запрос статуса платежа в API шлюза."""
    if is_test_mode():
        return None
    payment = _sdk().find_one(payment_id)
    return GatewayPayment(payment.id, payment.status)
