import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from yookassa.domain.notification import WebhookNotificationFactory

from orders.cart import Cart
from orders.models import Order, OrderItem

from . import gateway
from .models import PaymentLog
from .services import process_payment


@login_required
@require_POST
def checkout(request):
    cart = Cart(request)
    items = cart.items
    if not items:
        messages.error(request, 'Корзина пуста')
        return redirect('cart')
    with transaction.atomic():
        order = Order.objects.create(buyer=request.user,
                                     total=sum(lic.price for lic in items))
        for lic in items:
            OrderItem.objects.create(order=order, track_license=lic, price=lic.price)
    payment = gateway.create_payment(order, request.build_absolute_uri(
        reverse('payment_result', args=[order.id])))
    PaymentLog.objects.create(order=order, external_id=payment.id,
                              amount=order.total, status=payment.status)
    order.status = 'pending'
    order.save(update_fields=['status'])
    cart.clear()
    return redirect(payment.confirmation_url)


@csrf_exempt
@require_POST
def yookassa_webhook(request):
    try:
        event = WebhookNotificationFactory().create(json.loads(request.body))
    except Exception:
        return HttpResponseBadRequest()
    payment = gateway.find_payment(event.object.id)   # повторная проверка в API шлюза
    if payment is None or not PaymentLog.objects.filter(external_id=payment.id).exists():
        raise Http404
    process_payment(payment.id, payment.status)       # лицензии, ссылки, начисления
    return HttpResponse(status=200)


@login_required
def payment_result(request, order_id):
    order = get_object_or_404(Order, pk=order_id, buyer=request.user)
    log = order.payments.first()
    if log and order.status != 'paid' and not gateway.is_test_mode():
        # Уведомление может прийти позже возврата покупателя – уточняем статус сами
        payment = gateway.find_payment(log.external_id)
        order = process_payment(payment.id, payment.status)
    return render(request, 'payments/result.html', {'order': order})


@login_required
def test_payment(request, external_id):
    """Тестовая форма оплаты для работы без ключей ЮKassa."""
    if not gateway.is_test_mode():
        raise Http404
    log = get_object_or_404(PaymentLog.objects.select_related('order'),
                            external_id=external_id, order__buyer=request.user)
    if request.method == 'POST':
        status = 'succeeded' if request.POST.get('result') == 'pay' else 'canceled'
        process_payment(external_id, status)
        return redirect('payment_result', order_id=log.order_id)
    return render(request, 'payments/test_payment.html', {'log': log})
