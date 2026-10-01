from django.urls import reverse

from audio_shop.test_utils import ShopTestCase

from .models import User


class AccountTests(ShopTestCase):
    def test_register_with_existing_email(self):
        response = self.client.post(reverse('register'), {
            'username': 'new', 'email': 'buyer@test.ru', 'role': 'buyer',
            'password1': 'Pass-12345', 'password2': 'Pass-12345'})
        self.assertContains(response, 'Пользователь с таким e-mail уже существует')

    def test_register_author_creates_profile(self):
        self.client.post(reverse('register'), {
            'username': 'beatmaker', 'email': 'bm@test.ru', 'role': 'author',
            'stage_name': 'Beat Maker', 'password1': 'Pass-12345', 'password2': 'Pass-12345'})
        self.assertEqual(User.objects.get(username='beatmaker').author_profile.stage_name,
                         'Beat Maker')

    def test_wrong_password(self):
        response = self.client.post(reverse('login'), {'username': 'buyer', 'password': 'bad'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_blocked_user_cannot_login(self):
        User.objects.filter(pk=self.buyer.pk).update(is_blocked=True)
        response = self.client.post(reverse('login'),
                                    {'username': 'buyer', 'password': 'Pass-12345'})
        self.assertContains(response, 'Учётная запись заблокирована')
