import secrets
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from accounts.models import AuthorProfile
from catalog.models import Status, Track, TrackLicense
from downloads.models import DownloadLink
from royalties.models import Royalty


def author_reward(price):
    """Вознаграждение автора: В = Ц × (1 – К)."""
    return (price * (1 - settings.PLATFORM_FEE)).quantize(Decimal('0.01'))


@transaction.atomic
def complete_order(order):
    """Вызывается после подтверждения оплаты платёжным шлюзом."""
    order.status = 'paid'
    order.save(update_fields=['status'])
    for item in order.items.select_related('track_license__track__author',
                                           'track_license__license_type'):
        lic = item.track_license
        # 1. Защищённая ссылка на скачивание
        DownloadLink.objects.create(
            order_item=item,
            token=secrets.token_urlsafe(32),
            expires_at=timezone.now() + timedelta(seconds=settings.DOWNLOAD_LINK_TTL),
            max_downloads=settings.DOWNLOAD_LIMIT,
        )
        # 2. Начисление вознаграждения автору
        amount = author_reward(item.price)
        Royalty.objects.create(author=lic.track.author, order_item=item, amount=amount)
        AuthorProfile.objects.filter(pk=lic.track.author_id).update(
            balance=F('balance') + amount)
        # 3. Эксклюзивная лицензия снимает трек с продажи и убирает его из каталога
        if lic.license_type.is_exclusive:
            TrackLicense.objects.filter(track=lic.track).update(is_available=False)
            Track.objects.filter(pk=lic.track_id).update(
                status=Status.objects.get(name=Status.SOLD_EXCLUSIVE))
    # 4. Письмо покупателю со ссылкой на раздел «Мои покупки» – после фиксации транзакции
    transaction.on_commit(lambda: send_purchase_email(order))


def send_purchase_email(order):
    lines = [f'{item.track_license.track.title} – {item.track_license.license_type.name}'
             for item in order.items.select_related('track_license__track',
                                                    'track_license__license_type')]
    send_mail(
        subject=f'Soundahahahha: заказ №{order.pk} оплачен',
        message='Спасибо за покупку!\n\n' + '\n'.join(lines) +
                f'\n\nСкачать файлы можно в разделе «Мои покупки»: {settings.SITE_URL}/accounts/profile/\n'
                'Ссылка действует 24 часа, не более 3 скачиваний.',
        from_email=None, recipient_list=[order.buyer.email], fail_silently=True)
