from decimal import Decimal

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from accounts.forms import AuthorProfileForm
from accounts.models import AuthorProfile

from .models import Payout


class PayoutForm(forms.Form):
    amount = forms.DecimalField(label='Сумма, руб.', min_value=Decimal('100'),
                                max_digits=12, decimal_places=2)


@login_required
@role_required('author')
def payouts(request):
    """Баланс автора, реквизиты и заявки на выплату."""
    author = request.user.author_profile
    form = PayoutForm(request.POST or None)
    profile_form = AuthorProfileForm(instance=author)
    if request.method == 'POST' and form.is_valid():
        amount = form.cleaned_data['amount']
        reserved = author.payouts.filter(status='requested').aggregate(s=Sum('amount'))['s'] or 0
        if not author.payout_details:
            messages.error(request, 'Укажите реквизиты для выплат')
        elif amount > author.balance - reserved:
            messages.error(request, 'Недостаточно средств на балансе')
        else:
            Payout.objects.create(author=author, amount=amount)
            messages.success(request, 'Заявка на выплату отправлена')
            return redirect('payouts')
    return render(request, 'royalties/payouts.html', {
        'author': author, 'form': form, 'profile_form': profile_form,
        'payouts': author.payouts.all(),
    })


@login_required
@role_required('author')
@require_POST
def update_details(request):
    form = AuthorProfileForm(request.POST, instance=request.user.author_profile)
    if form.is_valid():
        form.save()
        messages.success(request, 'Данные профиля сохранены')
    return redirect('payouts')


@login_required
@role_required('admin')
def payouts_admin(request):
    return render(request, 'royalties/payouts_admin.html', {
        'payouts': Payout.objects.select_related('author').order_by('status', '-requested_at'),
    })


@login_required
@role_required('admin')
@require_POST
def process_payout(request, pk, action):
    with transaction.atomic():
        payout = get_object_or_404(Payout.objects.select_for_update(), pk=pk, status='requested')
        if action == 'approve':
            # Списание с проверкой баланса в одном запросе
            ok = AuthorProfile.objects.filter(pk=payout.author_id, balance__gte=payout.amount) \
                .update(balance=F('balance') - payout.amount)
            if not ok:
                messages.error(request, 'Недостаточно средств на балансе автора')
                return redirect('payouts_admin')
            payout.status = 'paid'
        else:
            payout.status = 'rejected'
        payout.processed_at = timezone.now()
        payout.save(update_fields=['status', 'processed_at'])
    messages.success(request, f'Заявка №{payout.pk}: {payout.get_status_display().lower()}')
    return redirect('payouts_admin')
