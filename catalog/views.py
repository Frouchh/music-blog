from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from datetime import timedelta

from django.db.models import Avg, Count, Min, Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from orders.models import OrderItem
from royalties.models import Royalty

from .forms import (AlbumForm, CatalogFilterForm, ReviewForm, TrackEditForm,
                    TrackLicenseFormSet, TrackUploadForm)
from .models import Album, Genre, LicenseType, Status, Track
from .services import make_preview


def published_tracks():
    return (Track.objects.filter(status__name=Status.PUBLISHED)
            .select_related('author', 'genre')
            .annotate(price_from=Min('licenses__price', filter=Q(licenses__is_available=True)),
                      rating=Avg('reviews__rating'))
            .order_by('-created_at'))


def catalog(request):
    """Главная страница: каталог с поиском, фильтрацией и сортировкой."""
    form = CatalogFilterForm(request.GET or None)
    tracks = published_tracks()
    if form.is_valid():
        data = form.cleaned_data
        if data['q']:
            tracks = tracks.filter(Q(title__icontains=data['q']) |
                                   Q(author__stage_name__icontains=data['q']))
        if data['genre']:
            tracks = tracks.filter(genre_id=data['genre'])
        if data['license']:
            tracks = tracks.filter(licenses__license_type_id=data['license'],
                                   licenses__is_available=True)
        if data['price_min'] is not None:
            tracks = tracks.filter(price_from__gte=data['price_min'])
        if data['price_max'] is not None:
            tracks = tracks.filter(price_from__lte=data['price_max'])
        order = {'price': 'price_from', '-price': '-price_from',
                 'rating': '-rating'}.get(data['sort'])
        if order:
            tracks = tracks.order_by(order)
    page = Paginator(tracks, 12).get_page(request.GET.get('page'))
    return render(request, 'catalog/catalog.html', {
        'form': form, 'page': page, 'genres': Genre.objects.all(),
        'license_types': LicenseType.objects.all(),
    })


def rules(request):
    """Правила площадки и лицензионные соглашения."""
    return render(request, 'catalog/rules.html', {'license_types': LicenseType.objects.all()})


def track_detail(request, pk):
    track = get_object_or_404(Track.objects.select_related('author', 'genre', 'status'), pk=pk)
    user = request.user
    is_owner = user.is_authenticated and track.author.user_id == user.id
    if track.status.name != Status.PUBLISHED and not (is_owner or user.is_authenticated and user.is_shop_admin):
        messages.error(request, 'Трек недоступен')
        return redirect('catalog')

    can_review = False
    if user.is_authenticated:
        can_review = OrderItem.objects.filter(
            order__buyer=user, order__status='paid', track_license__track=track
        ).exists() and not track.reviews.filter(user=user).exists()

    return render(request, 'catalog/track_detail.html', {
        'track': track,
        'licenses': track.licenses.select_related('license_type').order_by('price'),
        'reviews': track.reviews.select_related('user'),
        'rating': track.reviews.aggregate(avg=Avg('rating'), cnt=Count('id')),
        'review_form': ReviewForm() if can_review else None,
    })


def album_detail(request, pk):
    album = get_object_or_404(Album, pk=pk)
    tracks = published_tracks().filter(album=album)
    return render(request, 'catalog/album_detail.html', {'album': album, 'tracks': tracks})


@login_required
@require_POST
def add_review(request, pk):
    track = get_object_or_404(Track, pk=pk)
    bought = OrderItem.objects.filter(order__buyer=request.user, order__status='paid',
                                      track_license__track=track).exists()
    form = ReviewForm(request.POST)
    if bought and form.is_valid() and not track.reviews.filter(user=request.user).exists():
        review = form.save(commit=False)
        review.user, review.track = request.user, track
        review.save()
        messages.success(request, 'Спасибо за отзыв')
    else:
        messages.error(request, 'Оставить отзыв может только покупатель трека')
    return redirect('track_detail', pk=pk)


@login_required
@role_required('author')
def upload_track(request):
    author = request.user.author_profile
    form = TrackUploadForm(request.POST or None, request.FILES or None, author=author)
    formset = TrackLicenseFormSet(
        request.POST or None, prefix='lic',
        initial=[{'license_type': lt.pk} for lt in LicenseType.objects.all()])
    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        track = form.save(commit=False)
        track.author = author
        track.status = Status.objects.get(name=Status.PENDING)
        track.save()
        make_preview(track)            # формирование 30-секундного демофрагмента
        formset.instance = track
        formset.save()                 # цены по видам лицензий
        messages.success(request, 'Трек отправлен на модерацию')
        return redirect('author_tracks')
    return render(request, 'catalog/upload.html', {'form': form, 'formset': formset})


@login_required
@role_required('author')
def edit_prices(request, pk):
    track = get_object_or_404(Track, pk=pk, author=request.user.author_profile)
    formset = TrackLicenseFormSet(request.POST or None, instance=track, prefix='lic')
    if request.method == 'POST' and formset.is_valid():
        formset.save()
        messages.success(request, 'Цены сохранены')
        return redirect('author_tracks')
    return render(request, 'catalog/edit_prices.html', {'track': track, 'formset': formset})


@login_required
@role_required('author')
def edit_track(request, pk):
    track = get_object_or_404(Track, pk=pk, author=request.user.author_profile)
    form = TrackEditForm(request.POST or None, request.FILES or None, instance=track)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Сведения о треке сохранены')
        return redirect('author_tracks')
    return render(request, 'catalog/edit_track.html', {'track': track, 'form': form})


@login_required
@role_required('author')
def create_album(request):
    form = AlbumForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        album = form.save(commit=False)
        album.author = request.user.author_profile
        album.status = Status.objects.get(name=Status.PUBLISHED)
        album.save()
        messages.success(request, f'Альбом «{album.title}» создан')
        return redirect('author_tracks')
    return render(request, 'catalog/album_form.html', {'form': form})


def sales_chart(author, months=6):
    """Начисления автора по месяцам для столбчатой диаграммы кабинета."""
    today = timezone.localdate().replace(day=1)
    starts = []
    for _ in range(months):
        starts.insert(0, today)
        today = (today - timedelta(days=1)).replace(day=1)
    rows = (Royalty.objects.filter(author=author, created_at__date__gte=starts[0])
            .annotate(month=TruncMonth('created_at')).values('month')
            .annotate(total=Sum('amount')))
    by_month = {r['month'].date(): r['total'] for r in rows}
    peak = max(by_month.values(), default=0) or 1
    return [{'label': m.strftime('%m.%Y'), 'total': by_month.get(m, 0),
             'height': int(by_month.get(m, 0) / peak * 100)} for m in starts]


@login_required
@role_required('author')
def author_tracks(request):
    """Кабинет автора: треки, статусы модерации, статистика продаж и баланс."""
    author = request.user.author_profile
    tracks = (Track.objects.filter(author=author).select_related('status', 'genre')
              .annotate(sales=Count('licenses__orderitem__royalty'),
                        earned=Sum('licenses__orderitem__royalty__amount')))
    totals = Royalty.objects.filter(author=author).aggregate(cnt=Count('id'), sum=Sum('amount'))
    chart = sales_chart(author)
    return render(request, 'catalog/author_tracks.html', {
        'author': author, 'tracks': tracks, 'totals': totals, 'chart': chart,
        'albums': author.albums.annotate(cnt=Count('tracks')),
        'royalties': Royalty.objects.filter(author=author)
                     .select_related('order_item__track_license__track')[:10],
    })
