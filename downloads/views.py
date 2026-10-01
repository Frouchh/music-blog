from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import F
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import DownloadLink


@login_required
def download(request, token):
    link = get_object_or_404(DownloadLink.objects.select_related(
        'order_item__order', 'order_item__track_license__track'), token=token)
    # Ссылка принадлежит покупателю и заказ оплачен
    if link.order_item.order.buyer_id != request.user.id \
            or link.order_item.order.status != 'paid':
        raise PermissionDenied
    if link.expires_at < timezone.now():
        return render(request, 'downloads/expired.html', status=410)
    # Атомарное увеличение счётчика с проверкой лимита
    updated = DownloadLink.objects.filter(
        pk=link.pk, downloads_count__lt=F('max_downloads')
    ).update(downloads_count=F('downloads_count') + 1)
    if not updated:
        return render(request, 'downloads/limit.html', status=403)
    track = link.order_item.track_license.track
    suffix = Path(track.audio_file.name).suffix
    return FileResponse(track.audio_file.open('rb'), as_attachment=True,
                        filename=f'{track.title}{suffix}')
