from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from accounts.models import User
from catalog.models import Status, Track
from orders.models import Order
from royalties.models import Royalty


@login_required
@role_required('admin')
def queue(request):
    """Очередь модерации: треки со статусом «На модерации»."""
    return render(request, 'moderation/queue.html', {
        'pending': Track.objects.filter(status__name=Status.PENDING)
                   .select_related('author', 'genre').order_by('created_at'),
        'recent': Track.objects.exclude(status__name=Status.PENDING)
                  .select_related('author', 'status')[:20],
    })


@login_required
@role_required('admin')
@require_POST
def moderate(request, pk, action):
    track = get_object_or_404(Track, pk=pk)
    comment = request.POST.get('comment', '').strip()
    if action == 'approve':
        track.status = Status.objects.get(name=Status.PUBLISHED)
    elif action == 'reject':
        if not comment:
            messages.error(request, 'При отклонении укажите причину')
            return redirect('moderation_queue')
        track.status = Status.objects.get(name=Status.REJECTED)
    elif action == 'withdraw':
        track.status = Status.objects.get(name=Status.WITHDRAWN)
    else:
        return redirect('moderation_queue')
    track.moderation_comment = comment
    track.save(update_fields=['status', 'moderation_comment'])
    messages.success(request, f'«{track.title}»: {track.status.name.lower()}')
    return redirect('moderation_queue')


@login_required
@role_required('admin')
def users(request):
    return render(request, 'moderation/users.html', {
        'users': User.objects.select_related('role').order_by('username'),
    })


@login_required
@role_required('admin')
@require_POST
def toggle_block(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user != request.user:
        user.is_blocked = not user.is_blocked
        user.save(update_fields=['is_blocked'])
    return redirect('moderation_users')


@login_required
@role_required('admin')
def report(request):
    """Отчёт о продажах: выручка, выплаты авторам, комиссия площадки."""
    sales = Order.objects.filter(status='paid').aggregate(cnt=Count('id'), sum=Sum('total'))
    royalties = Royalty.objects.aggregate(sum=Sum('amount'))['sum'] or 0
    revenue = sales['sum'] or 0
    top = (Track.objects.annotate(sold=Count('licenses__orderitem__royalty'))
           .filter(sold__gt=0).select_related('author').order_by('-sold')[:10])
    return render(request, 'moderation/report.html', {
        'orders_count': sales['cnt'], 'revenue': revenue,
        'royalties': royalties, 'fee': revenue - royalties, 'top': top,
    })
