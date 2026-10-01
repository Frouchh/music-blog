from django.db import transaction

from orders.models import Order
from orders.services import complete_order

from .models import PaymentLog


@transaction.atomic
def process_payment(external_id, status):
    """Обновляет журнал и завершает заказ. Повторное уведомление ничего не меняет."""
    log = PaymentLog.objects.select_for_update().get(external_id=external_id)
    log.status = status
    log.save(update_fields=['status', 'updated_at'])
    order = Order.objects.select_for_update().get(pk=log.order_id)
    if status == 'succeeded' and order.status != 'paid':
        complete_order(order)          # ссылки, начисления, эксклюзив
    return order
