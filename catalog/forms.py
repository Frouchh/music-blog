from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from .models import Album, Review, Track, TrackLicense


class TrackUploadForm(forms.ModelForm):
    rights_confirmed = forms.BooleanField(
        label='Подтверждаю, что являюсь автором или правообладателем трека',
        error_messages={'required': 'Без подтверждения прав трек не может быть опубликован'})

    class Meta:
        model = Track
        fields = ['title', 'genre', 'album', 'description', 'cover', 'audio_file']
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, author=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['album'].queryset = Album.objects.filter(author=author)
        self.fields['audio_file'].widget.attrs['accept'] = '.mp3,.wav'

    def clean_audio_file(self):
        f = self.cleaned_data['audio_file']
        ext = f.name.rsplit('.', 1)[-1].lower()
        if ext not in settings.ALLOWED_AUDIO_EXT:
            raise ValidationError('Допустимы только файлы MP3 и WAV')
        if f.size > settings.MAX_AUDIO_SIZE:
            raise ValidationError('Размер файла не должен превышать 50 МБ')
        return f


class TrackLicenseForm(forms.ModelForm):
    class Meta:
        model = TrackLicense
        fields = ['license_type', 'price', 'is_available']


TrackLicenseFormSet = inlineformset_factory(
    Track, TrackLicense, form=TrackLicenseForm, extra=3, max_num=3, can_delete=False)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {'rating': forms.Select(choices=[(i, '★' * i) for i in range(5, 0, -1)]),
                   'text': forms.Textarea(attrs={'rows': 3})}


class CatalogFilterForm(forms.Form):
    SORT_CHOICES = [('new', 'Сначала новые'), ('popular', 'Популярные'), ('price', 'Сначала дешёвые'),
                    ('-price', 'Сначала дорогие'), ('rating', 'По рейтингу')]

    q = forms.CharField(required=False, label='Поиск')
    genre = forms.IntegerField(required=False)
    license = forms.IntegerField(required=False)
    price_min = forms.DecimalField(required=False, min_value=0, label='Цена от')
    price_max = forms.DecimalField(required=False, min_value=0, label='до')
    sort = forms.ChoiceField(required=False, choices=SORT_CHOICES)


class TrackEditForm(forms.ModelForm):
    """Редактирование сведений о треке без замены аудиофайла."""
    class Meta:
        model = Track
        fields = ['title', 'genre', 'album', 'description', 'cover']
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['album'].queryset = Album.objects.filter(author=self.instance.author)


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'cover']
