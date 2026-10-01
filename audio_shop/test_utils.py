"""Общие данные для автотестов."""
import io
import shutil
import tempfile
import wave
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from accounts.models import AuthorProfile, Role, User
from catalog.models import Genre, LicenseType, Status, Track, TrackLicense


def wav_bytes(seconds=1):
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(b'\x00\x00' * 8000 * seconds)
    return buf.getvalue()


class ShopTestCase(TestCase):
    """Создаёт покупателя, автора, администратора и опубликованный трек с тремя лицензиями."""

    @classmethod
    def setUpClass(cls):
        cls._media = tempfile.mkdtemp()
        cls._protected = tempfile.mkdtemp()
        cls._override = override_settings(MEDIA_ROOT=cls._media,
                                          PROTECTED_MEDIA_ROOT=cls._protected)
        cls._override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._override.disable()
        shutil.rmtree(cls._media, ignore_errors=True)
        shutil.rmtree(cls._protected, ignore_errors=True)

    @classmethod
    def setUpTestData(cls):
        cls.buyer = User.objects.create_user('buyer', 'buyer@test.ru', 'Pass-12345',
                                             role=Role.objects.get(name=Role.BUYER))
        cls.other = User.objects.create_user('other', 'other@test.ru', 'Pass-12345',
                                             role=Role.objects.get(name=Role.BUYER))
        cls.author_user = User.objects.create_user('author', 'author@test.ru', 'Pass-12345',
                                                   role=Role.objects.get(name=Role.AUTHOR))
        cls.author = AuthorProfile.objects.create(user=cls.author_user, stage_name='DJ Test',
                                                  payout_details='Карта 2200 0000 0000 0000')
        cls.admin = User.objects.create_user('admin', 'admin@test.ru', 'Pass-12345',
                                             role=Role.objects.get(name=Role.ADMIN))
        cls.track = Track.objects.create(
            author=cls.author, genre=Genre.objects.first(),
            status=Status.objects.get(name=Status.PUBLISHED), title='Night Drive',
            audio_file=SimpleUploadedFile('night.wav', wav_bytes()))
        prices = {'Личная': Decimal('149'), 'Коммерческая': Decimal('990'),
                  'Эксклюзивная': Decimal('9900')}
        cls.licenses = {
            lt.name: TrackLicense.objects.create(track=cls.track, license_type=lt,
                                                 price=prices[lt.name])
            for lt in LicenseType.objects.all()
        }
