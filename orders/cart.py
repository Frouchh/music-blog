from decimal import Decimal

from catalog.models import Status, TrackLicense


class Cart:
    """Корзина хранится в сессии в виде списка номеров TrackLicense."""
    SESSION_KEY = 'cart'

    def __init__(self, request):
        self.session = request.session
        self.ids = self.session.get(self.SESSION_KEY, [])

    def save(self):
        self.session[self.SESSION_KEY] = self.ids
        self.session.modified = True

    def add(self, track_license):
        # В корзине может быть только одна лицензия на трек
        same_track = set(TrackLicense.objects.filter(pk__in=self.ids, track=track_license.track)
                         .values_list('pk', flat=True))
        self.ids = [i for i in self.ids if i not in same_track]
        self.ids.append(track_license.pk)
        self.save()

    def remove(self, license_id):
        self.ids = [i for i in self.ids if i != license_id]
        self.save()

    def clear(self):
        self.ids = []
        self.save()

    @property
    def items(self):
        """Только лицензии, которые всё ещё можно купить."""
        return list(TrackLicense.objects
                    .filter(pk__in=self.ids, is_available=True,
                            track__status__name=Status.PUBLISHED)
                    .select_related('track__author', 'license_type'))

    def total(self):
        return sum((lic.price for lic in self.items), Decimal('0'))

    def __len__(self):
        return len(self.ids)
