from decimal import Decimal

from django.urls import reverse

from accounts.models import AuthorProfile
from audio_shop.test_utils import ShopTestCase

from .models import Payout


class PayoutTests(ShopTestCase):
    def setUp(self):
        AuthorProfile.objects.filter(pk=self.author.pk).update(balance=Decimal('891'))

    def test_payout_more_than_balance(self):
        self.client.force_login(self.author_user)
        response = self.client.post(reverse('payouts'), {'amount': '1000'})
        self.assertContains(response, 'Недостаточно средств на балансе')
        self.assertFalse(Payout.objects.exists())

    def test_payout_approved_by_admin(self):
        self.client.force_login(self.author_user)
        self.client.post(reverse('payouts'), {'amount': '500'})
        payout = Payout.objects.get()
        self.client.force_login(self.admin)
        self.client.post(reverse('process_payout', args=[payout.pk, 'approve']))
        payout.refresh_from_db()
        self.assertEqual(payout.status, 'paid')
        self.assertEqual(AuthorProfile.objects.get(pk=self.author.pk).balance, Decimal('391'))
