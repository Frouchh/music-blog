import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from accounts.models import AuthorProfile

class ProtectedStorage(FileSystemStorage):
    """Полные аудиофайлы лежат вне публичного каталога media/ и не имеют URL."""
    base_url = None

    @property
    def base_location(self):
        return settings.PROTECTED_MEDIA_ROOT

    @property
    def location(self):
        return os.path.abspath(self.base_location)


protected_storage = ProtectedStorage()


class Genre(models.Model):
    name = models.CharField('Жанр', max_length=50, unique=True)

    class Meta:
        db_table = 'genres'
        ordering = ['name']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Status(models.Model):
    """Справочник статусов модерации."""
    PENDING = 'На модерации'
    PUBLISHED = 'Опубликован'
    REJECTED = 'Отклонён'
    WITHDRAWN = 'Снят с продажи'

    name = models.CharField('Статус', max_length=30, unique=True)

    class Meta:
        db_table = 'statuses'
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

    def __str__(self):
        return self.name


class Album(models.Model):
    author = models.ForeignKey(AuthorProfile, on_delete=models.CASCADE, related_name='albums')
    title = models.CharField('Название', max_length=100)
    cover = models.ImageField('Обложка', upload_to='covers/', blank=True)
    status = models.ForeignKey(Status, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'albums'
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбомы'

    def __str__(self):
        return self.title


class Track(models.Model):
    author = models.ForeignKey(AuthorProfile, on_delete=models.CASCADE, related_name='tracks')
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='tracks', verbose_name='Альбом')
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT, verbose_name='Жанр')
    status = models.ForeignKey(Status, on_delete=models.PROTECT)
    title = models.CharField('Название', max_length=100)
    description = models.TextField('Описание', blank=True)
    cover = models.ImageField('Обложка', upload_to='covers/', blank=True)
    audio_file = models.FileField('Аудиофайл (MP3, WAV)', storage=protected_storage,
                                  upload_to='tracks/')
    preview_file = models.FileField(upload_to='previews/', blank=True)
    duration = models.PositiveIntegerField('Длительность, с', default=0)
    moderation_comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tracks'
        ordering = ['-created_at']
        verbose_name = 'Трек'
        verbose_name_plural = 'Треки'

    def __str__(self):
        return self.title

    @property
    def duration_display(self):
        return f'{self.duration // 60}:{self.duration % 60:02d}'

    def min_price(self):
        prices = [lic.price for lic in self.licenses.all() if lic.is_available]
        return min(prices) if prices else None


class LicenseType(models.Model):
    name = models.CharField('Вид лицензии', max_length=50)
    description = models.TextField('Права покупателя')
    is_exclusive = models.BooleanField('Эксклюзивная', default=False)

    class Meta:
        db_table = 'license_types'
        verbose_name = 'Вид лицензии'
        verbose_name_plural = 'Виды лицензий'

    def __str__(self):
        return self.name


class TrackLicense(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='licenses')
    license_type = models.ForeignKey(LicenseType, on_delete=models.PROTECT,
                                     verbose_name='Вид лицензии')
    price = models.DecimalField('Цена, руб.', max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(1)])
    is_available = models.BooleanField('Доступна', default=True)

    class Meta:
        db_table = 'track_licenses'
        unique_together = ('track', 'license_type')
        verbose_name = 'Цена лицензии'
        verbose_name_plural = 'Цены лицензий'

    def __str__(self):
        return f'{self.track} – {self.license_type} ({self.price} руб.)'


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        'Оценка', validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField('Отзыв', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        unique_together = ('user', 'track')
        ordering = ['-created_at']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
