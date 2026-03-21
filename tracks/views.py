from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count
from .models import Track, Genre, User, Rating, Role
from datetime import datetime, timedelta
import json

def index(request):
    """Главная страница - только одобренные треки"""
    featured_tracks = Track.objects.filter(status='approved').select_related('user', 'genre').order_by('-date_publication')[:11]
    
    context = {
        'featured_tracks': featured_tracks,
    }
    return render(request, 'index.html', context)


def tracks_list(request):
    """Страница со всеми треками - только одобренные"""
    tracks = Track.objects.filter(status='approved').select_related('user', 'genre').order_by('-date_publication')
    genres = Genre.objects.all()
    
    context = {
        'tracks': tracks,
        'genres': genres,
    }
    return render(request, 'tracks.html', context)


def tracks_new(request):
    """Новые треки - только одобренные за последние 7 дней"""
    week_ago = datetime.now().date() - timedelta(days=7)
    tracks = Track.objects.filter(status='approved', date_publication__gte=week_ago).select_related('user', 'genre').order_by('-date_publication')
    genres = Genre.objects.all()
    
    context = {
        'tracks': tracks,
        'genres': genres,
    }
    return render(request, 'tracks_new.html', context)


def tracks_week(request):
    """Треки недели - только одобренные, наиболее оцениваемые за последние 7 дней"""
    week_ago = datetime.now().date() - timedelta(days=7)
    
    tracks = Track.objects.filter(status='approved', date_publication__gte=week_ago).annotate(
        avg_rating=Avg('rating__score_value'),
        rating_count=Count('rating')
    ).filter(rating_count__gt=0).order_by('-avg_rating')[:10]
    
    genres = Genre.objects.all()
    
    context = {
        'tracks': tracks,
        'genres': genres,
    }
    return render(request, 'tracks_week.html', context)


def track_detail(request, track_id):
    """Детальная страница трека"""
    track = get_object_or_404(Track.objects.select_related('user', 'genre'), track_id=track_id)
    
    # Проверяем доступ: если трек не одобрен, смотреть могут только админ или владелец
    if track.status != 'approved':
        user_id = request.session.get('user_id')
        is_admin = request.session.get('user_role') == 'admin'
        is_owner = user_id == track.user.user_id
        
        if not (is_admin or is_owner):
            messages.error(request, 'Этот трек еще не опубликован')
            return redirect('/')
    
    ratings = Rating.objects.filter(track=track)
    avg_rating = 0
    if ratings:
        avg_rating = sum(r.score_value for r in ratings) / len(ratings)
    
    user_rated = False
    user_score = None
    if 'user_id' in request.session:
        user_rating = Rating.objects.filter(user_id=request.session['user_id'], track=track).first()
        if user_rating:
            user_rated = True
            user_score = user_rating.score_value
    
    context = {
        'track': track,
        'avg_rating': round(avg_rating, 1),
        'user_rated': user_rated,
        'user_score': user_score,
    }
    return render(request, 'track.html', context)


def upload_track(request):
    """Публикация трека - отправляется на модерацию"""
    if 'user_id' not in request.session:
        messages.error(request, 'Сначала войдите в систему')
        return redirect('/login/')
    
    if request.method == 'POST':
        title = request.POST.get('track_name')
        author_name = request.POST.get('artist_name')
        genre_id = request.POST.get('genre')
        description = request.POST.get('description', '')
        audio_file = request.FILES.get('audio_file')
        
        if not title or not author_name or not genre_id:
            messages.error(request, 'Заполните все обязательные поля')
            return redirect('/upload/')
        
        if not audio_file:
            messages.error(request, 'Выберите аудиофайл')
            return redirect('/upload/')
        
        try:
            track = Track.objects.create(
                title=title,
                author_name=author_name,
                description=description,
                user_id=request.session['user_id'],
                genre_id=genre_id,
                audio_file=audio_file,
                status='pending'
            )
            messages.success(request, 'Трек отправлен на модерацию! После проверки он появится на сайте.')
            return redirect('/profile/')
        except Exception as e:
            messages.error(request, f'Ошибка при публикации: {str(e)}')
    
    genres = Genre.objects.all()
    context = {
        'genres': genres,
    }
    return render(request, 'upload.html', context)


def profile(request):
    """Личный кабинет - показываем все треки пользователя с их статусами"""
    if 'user_id' not in request.session:
        messages.error(request, 'Сначала войдите в систему')
        return redirect('/login/')
    
    user = get_object_or_404(User, user_id=request.session['user_id'])
    user_tracks = Track.objects.filter(user=user).order_by('-date_publication')
    
    context = {
        'user': user,
        'user_tracks': user_tracks,
    }
    return render(request, 'profile.html', context)


def admin_tracks(request):
    """Страница модерации для администратора"""
    if 'user_id' not in request.session:
        messages.error(request, 'Сначала войдите в систему')
        return redirect('/login/')
    
    user_role = request.session.get('user_role')
    if user_role != 'admin':
        messages.error(request, 'Доступ запрещен')
        return redirect('/')
    
    # Треки на модерации
    pending_tracks = Track.objects.filter(status='pending').select_related('user', 'genre')
    # Одобренные треки
    approved_tracks = Track.objects.filter(status='approved').select_related('user', 'genre').order_by('-date_publication')[:20]
    # Отклоненные треки
    rejected_tracks = Track.objects.filter(status='rejected').select_related('user', 'genre').order_by('-moderated_at')[:20]
    
    context = {
        'pending_tracks': pending_tracks,
        'approved_tracks': approved_tracks,
        'rejected_tracks': rejected_tracks,
    }
    return render(request, 'admin_tracks.html', context)


def moderate_track(request, track_id, action):
    """Модерация трека (админ)"""
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Не авторизован'}, status=401)
    
    user_role = request.session.get('user_role')
    if user_role != 'admin':
        return JsonResponse({'error': 'Доступ запрещен'}, status=403)
    
    track = get_object_or_404(Track, track_id=track_id)
    admin_user = get_object_or_404(User, user_id=request.session['user_id'])
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            comment = data.get('comment', '')
        except:
            comment = ''
        
        if action == 'approve':
            track.status = 'approved'
            message = 'Трек одобрен и опубликован на сайте'
        elif action == 'reject':
            track.status = 'rejected'
            message = 'Трек отклонен'
        else:
            return JsonResponse({'error': 'Неверное действие'}, status=400)
        
        track.moderation_comment = comment
        track.moderated_at = datetime.now()
        track.moderated_by = admin_user
        track.save()
        
        return JsonResponse({
            'success': True,
            'message': message,
            'status': track.status
        })
    
    return JsonResponse({'error': 'Метод не разрешен'}, status=405)


def register(request):
    """Регистрация"""
    if request.method == 'POST':
        login = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Пароли не совпадают')
            return redirect('/register/')
        
        if User.objects.filter(login=login).exists():
            messages.error(request, 'Пользователь с таким логином уже существует')
            return redirect('/register/')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
            return redirect('/register/')
        
        try:
            user_role = Role.objects.get(name='user')
        except Role.DoesNotExist:
            user_role = Role.objects.create(name='user')
        
        user = User.objects.create(
            login=login,
            password=make_password(password),
            email=email,
            role=user_role
        )
        
        messages.success(request, 'Регистрация успешна! Войдите в систему')
        return redirect('/login/')
    
    return render(request, 'register.html')


def user_login(request):
    """Вход"""
    if request.method == 'POST':
        login = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(login=login)
            if check_password(password, user.password):
                request.session['user_id'] = user.user_id
                request.session['user_login'] = user.login
                request.session['user_role'] = user.role.name
                messages.success(request, f'Добро пожаловать, {user.login}!')
                return redirect('/')
            else:
                messages.error(request, 'Неверный пароль')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден')
    
    return render(request, 'login.html')


def user_logout(request):
    """Выход"""
    request.session.flush()
    messages.success(request, 'Вы вышли из системы')
    return redirect('/')


def rate_track(request, track_id):
    """Оценка трека"""
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Необходимо авторизоваться'}, status=401)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            score = data.get('score')
            
            if not score or score < 1 or score > 10:
                return JsonResponse({'error': 'Оценка должна быть от 1 до 10'}, status=400)
            
            track = get_object_or_404(Track, track_id=track_id)
            user_id = request.session['user_id']
            
            rating, created = Rating.objects.update_or_create(
                user_id=user_id,
                track=track,
                defaults={'score_value': score}
            )
            
            ratings = Rating.objects.filter(track=track)
            avg_rating = sum(r.score_value for r in ratings) / len(ratings)
            
            return JsonResponse({
                'success': True,
                'avg_rating': round(avg_rating, 1),
                'message': 'Оценка сохранена!'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Метод не разрешен'}, status=405)