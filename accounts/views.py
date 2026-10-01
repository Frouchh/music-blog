from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from orders.models import Order

from .forms import LoginForm, RegisterForm


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Регистрация выполнена')
        return redirect('author_tracks' if user.is_author else 'catalog')
    return render(request, 'accounts/register.html', {'form': form})


class ShopLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm


@login_required
def profile(request):
    """Кабинет покупателя: заказы и купленные лицензии со ссылками на скачивание."""
    orders = (Order.objects.filter(buyer=request.user)
              .prefetch_related('items__track_license__track',
                                'items__track_license__license_type',
                                'items__download_link')
              .order_by('-created_at'))
    return render(request, 'accounts/profile.html', {'orders': orders})
