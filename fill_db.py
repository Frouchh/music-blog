import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'music_blog.settings')
django.setup()

from tracks.models import Role, Genre, User, Track
from django.contrib.auth.hashers import make_password

print('Заполняю базу данных...')

# Создаем роли
admin_role, _ = Role.objects.get_or_create(name='admin')
user_role, _ = Role.objects.get_or_create(name='user')
print('✓ Роли созданы')

# Создаем жанры
genres = ['Phonk', 'House', 'Techno', 'Hip-Hop']
for genre_name in genres:
    Genre.objects.get_or_create(name=genre_name)
    print(f'  - Жанр: {genre_name}')

# Создаем пользователей
test_user, created = User.objects.get_or_create(
    login='testuser',
    defaults={
        'email': 'test@example.com',
        'password': make_password('test123'),
        'role': user_role
    }
)
print('✓ Пользователь: testuser / test123')

admin_user, created = User.objects.get_or_create(
    login='admin',
    defaults={
        'email': 'admin@musicblog.com',
        'password': make_password('admin123'),
        'role': admin_role
    }
)
print('✓ Администратор: admin / admin123')

# Получаем жанры
phonk = Genre.objects.get(name='Phonk')
house = Genre.objects.get(name='House')
techno = Genre.objects.get(name='Techno')
hiphop = Genre.objects.get(name='Hip-Hop')

# Создаем треки
tracks_data = [
    {'title': 'Midnight Drive', 'author': 'Electro Wave', 'genre': phonk, 
     'desc': 'Атмосферный трек для ночных поездок.'},
    {'title': 'Neon Lights', 'author': 'Synth City', 'genre': house, 
     'desc': 'Энергичный трек с яркими мелодиями.'},
    {'title': 'Deep Space', 'author': 'Cosmic Beats', 'genre': techno, 
     'desc': 'Космическое путешествие через звуки техно.'},
    {'title': 'Urban Flow', 'author': 'City Rhythms', 'genre': hiphop, 
     'desc': 'Уличные ритмы и плавные биты.'},
]

for track_data in tracks_data:
    track, created = Track.objects.get_or_create(
        title=track_data['title'],
        defaults={
            'author_name': track_data['author'],
            'description': track_data['desc'],
            'user': test_user,
            'genre': track_data['genre']
        }
    )
    if created:
        print(f'  - Трек: {track.title}')

print('\n✅ База данных успешно заполнена!')