"""Заполнение базы демонстрационными данными: python manage.py seed_demo"""
import math
import struct
import wave
from decimal import Decimal
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from accounts.models import AuthorProfile, Role, User
from catalog.models import Album, Genre, LicenseType, Status, Track, TrackLicense
from catalog.services import make_preview

TRACKS = [
    ('Night Drive', 'Электроника', 'Ночной синтвейв с тёплым басом.', 220),
    ('Cold Streets', 'Phonk', 'Мрачный фонк с ковбеллом для роликов.', 330),
    ('Sunrise', 'Lo-fi', 'Спокойный lo-fi бит для подкастов и стримов.', 262),
    ('Warehouse', 'Techno', 'Ровный техно-грув 128 BPM.', 196),
    ('Deep Blue', 'House', 'Глубокий хаус с вокальными чопами.', 247),
    ('Skyline', 'Эмбиент', 'Атмосферный эмбиент для фона.', 174),
]
PENDING = ('Rainy Window', 'Lo-fi', 'Медленный lo-fi с шумом дождя.', 294)
PRICES = {'Личная': Decimal('149'), 'Коммерческая': Decimal('990'),
          'Эксклюзивная': Decimal('9900')}


def tone_wav(freq, seconds=40, rate=22050):
    buf = BytesIO()
    with wave.open(buf, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        frames = b''.join(
            struct.pack('<h', int(8000 * math.sin(2 * math.pi * freq * i / rate)))
            for i in range(rate * seconds))
        w.writeframes(frames)
    return buf.getvalue()


class Command(BaseCommand):
    help = 'Создаёт демонстрационных пользователей и треки'

    def handle(self, *args, **options):
        roles = {r.name: r for r in Role.objects.all()}

        def user(login, role, password='Demo-12345', **extra):
            obj, created = User.objects.get_or_create(
                username=login, defaults={'email': f'{login}@demo.ru', 'role': roles[role], **extra})
            if created:
                obj.set_password(password)
                obj.save()
            return obj

        user('admin', Role.ADMIN, is_staff=True, is_superuser=True)
        user('buyer', Role.BUYER)
        author_user = user('author', Role.AUTHOR)
        author, _ = AuthorProfile.objects.get_or_create(
            user=author_user, defaults={'stage_name': 'Frouchh',
                                        'payout_details': 'Карта 2200 **** **** 0000'})

        published = Status.objects.get(name=Status.PUBLISHED)
        album, _ = Album.objects.get_or_create(author=author, title='Night Session',
                                               defaults={'status': published})
        for title, genre, description, freq in TRACKS + [PENDING]:
            if Track.objects.filter(title=title).exists():
                continue
            status = published if title != PENDING[0] else Status.objects.get(name=Status.PENDING)
            track = Track(author=author, genre=Genre.objects.get(name=genre),
                          status=status, title=title, description=description,
                          album=album if title in ('Night Drive', 'Deep Blue') else None)
            track.audio_file.save(f'{title.lower().replace(" ", "_")}.wav',
                                  ContentFile(tone_wav(freq)), save=False)
            track.save()
            make_preview(track)
            for lt in LicenseType.objects.all():
                TrackLicense.objects.create(track=track, license_type=lt, price=PRICES[lt.name])
        self.stdout.write(self.style.SUCCESS(
            'Готово. Учётные записи: admin / author / buyer, пароль Demo-12345'))
