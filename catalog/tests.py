from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse

from audio_shop.test_utils import ShopTestCase, wav_bytes
from catalog.models import LicenseType, Status, Track


class UploadTests(ShopTestCase):
    def upload(self, name, content):
        self.client.force_login(self.author_user)
        data = {'title': 'New', 'genre': self.track.genre_id, 'description': '',
                'audio_file': SimpleUploadedFile(name, content),
                'lic-TOTAL_FORMS': 3, 'lic-INITIAL_FORMS': 0}
        for i, lt in enumerate(LicenseType.objects.all()):
            data[f'lic-{i}-license_type'] = lt.pk
            data[f'lic-{i}-price'] = 100 * (i + 1)
            data[f'lic-{i}-is_available'] = 'on'
        return self.client.post(reverse('upload_track'), data)

    def test_wrong_format(self):
        response = self.upload('song.flac', b'fLaC')
        self.assertContains(response, 'Допустимы только файлы MP3 и WAV')

    @override_settings(MAX_AUDIO_SIZE=1000)
    def test_too_big(self):
        response = self.upload('big.wav', wav_bytes())
        self.assertContains(response, 'Размер файла не должен превышать 50 МБ')

    def test_upload_goes_to_moderation(self):
        response = self.upload('new.wav', wav_bytes(2))
        self.assertRedirects(response, reverse('author_tracks'))
        track = Track.objects.get(title='New')
        self.assertEqual(track.status.name, Status.PENDING)
        self.assertEqual(track.licenses.count(), 3)
        self.assertEqual(track.duration, 2)

    def test_buyer_cannot_upload(self):
        self.client.force_login(self.buyer)
        self.assertEqual(self.client.get(reverse('upload_track')).status_code, 403)


class CatalogTests(ShopTestCase):
    def test_filter_by_price(self):
        response = self.client.get(reverse('catalog'), {'price_max': 100})
        self.assertNotContains(response, 'Night Drive')
        response = self.client.get(reverse('catalog'), {'price_max': 200, 'q': 'night'})
        self.assertContains(response, 'Night Drive')

    def test_pending_track_hidden(self):
        Track.objects.update(status=Status.objects.get(name=Status.PENDING))
        self.assertNotContains(self.client.get(reverse('catalog')), 'Night Drive')
        response = self.client.get(reverse('track_detail', args=[self.track.pk]))
        self.assertRedirects(response, reverse('catalog'))

    def test_moderation_approve(self):
        Track.objects.update(status=Status.objects.get(name=Status.PENDING))
        self.client.force_login(self.admin)
        self.client.post(reverse('moderate', args=[self.track.pk, 'approve']))
        self.track.refresh_from_db()
        self.assertEqual(self.track.status.name, Status.PUBLISHED)

    def test_buyer_has_no_admin_access(self):
        self.client.force_login(self.buyer)
        self.assertEqual(self.client.get(reverse('moderation_queue')).status_code, 403)
