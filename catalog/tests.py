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
                'rights_confirmed': 'on', 'lic-TOTAL_FORMS': 3, 'lic-INITIAL_FORMS': 0}
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

    def test_preview_without_ffmpeg(self):
        import builtins
        real_import = builtins.__import__

        def no_pydub(name, *args, **kwargs):
            if name.startswith('pydub'):
                raise ImportError('нет FFmpeg')
            return real_import(name, *args, **kwargs)

        from unittest import mock
        with mock.patch('builtins.__import__', side_effect=no_pydub):
            self.upload('long.wav', wav_bytes(40))
        track = Track.objects.get(title='New')
        self.assertTrue(track.preview_file.name.endswith('.wav'))
        import wave
        with wave.open(track.preview_file.path) as w:
            self.assertEqual(round(w.getnframes() / w.getframerate()), 30)

    def test_rights_confirmation_required(self):
        self.client.force_login(self.author_user)
        response = self.client.post(reverse('upload_track'), {'title': 'X'})
        self.assertContains(response, 'Без подтверждения прав трек не может быть опубликован')

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

    def test_filter_by_license(self):
        from catalog.models import LicenseType, TrackLicense
        exclusive = LicenseType.objects.get(is_exclusive=True)
        response = self.client.get(reverse('catalog'), {'license': exclusive.pk})
        self.assertContains(response, 'Night Drive')
        TrackLicense.objects.filter(license_type=exclusive).update(is_available=False)
        response = self.client.get(reverse('catalog'), {'license': exclusive.pk})
        self.assertNotContains(response, 'Night Drive')

    def test_rules_page(self):
        self.assertContains(self.client.get(reverse('rules')), 'Эксклюзивная')

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


class AuthorCabinetTests(ShopTestCase):
    def test_edit_track(self):
        self.client.force_login(self.author_user)
        self.client.post(reverse('edit_track', args=[self.track.pk]),
                         {'title': 'Night Drive 2', 'genre': self.track.genre_id, 'description': 'new'})
        self.track.refresh_from_db()
        self.assertEqual(self.track.title, 'Night Drive 2')

    def test_foreign_track_cannot_be_edited(self):
        from accounts.models import AuthorProfile, Role, User
        user = User.objects.create_user('a2', 'a2@test.ru', 'Pass-12345',
                                        role=Role.objects.get(name=Role.AUTHOR))
        AuthorProfile.objects.create(user=user, stage_name='Other')
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse('edit_track', args=[self.track.pk])).status_code, 404)

    def test_create_album(self):
        self.client.force_login(self.author_user)
        self.client.post(reverse('create_album'), {'title': 'First EP'})
        self.assertTrue(self.author.albums.filter(title='First EP').exists())
