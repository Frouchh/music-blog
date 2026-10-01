from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Status, TrackLicense

from .cart import Cart


def cart_detail(request):
    cart = Cart(request)
    items = cart.items
    if len(items) != len(cart):          # часть лицензий успели снять с продажи
        cart.ids = [lic.pk for lic in items]
        cart.save()
        messages.warning(request, 'Некоторые позиции больше недоступны и удалены из корзины')
    return render(request, 'orders/cart.html', {'items': items, 'total': cart.total()})


@require_POST
def cart_add(request):
    lic = get_object_or_404(TrackLicense, pk=request.POST.get('license_id'),
                            is_available=True, track__status__name=Status.PUBLISHED)
    cart = Cart(request)
    cart.add(lic)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'count': len(cart)})
    messages.success(request, f'«{lic.track}» ({lic.license_type}) добавлен в корзину')
    if request.POST.get('buy_now'):
        return redirect('cart')
    return redirect('track_detail', pk=lic.track_id)


@require_POST
def cart_remove(request, license_id):
    Cart(request).remove(license_id)
    return redirect('cart')
