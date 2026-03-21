from django.core.management.base import BaseCommand
from tracks.models import Role, Genre, User, Track
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Заполняет базу данных начальными данными'

    def handle(self, *args, **options):
        self.stdout.write('Начинаю заполнение базы данных...')
        
        # Создаем роли
        admin_role, _ = Role.objects.get_or_create(name='admin')
        user_role, _ = Role.objects.get_or_create(name='user')
        self.stdout.write('✓ Роли созданы')
        
        # Создаем жанры
        genres = ['Phonk', 'House', 'Techno', 'Hip-Hop']
        for genre_name in genres:
            Genre.objects.get_or_create(name=genre_name)
            self.stdout.write(f'  - Создан жанр: {genre_name}')
        
        # Создаем пользователей
        test_user, created = User.objects.get_or_create(
            login='testuser',
            defaults={
                'email': 'test@example.com',
                'password': make_password('test123'),
                'role': user_role
            }
        )
        self.stdout.write('✓ Создан пользователь: testuser / test123')
        
        admin_user, created = User.objects.get_or_create(
            login='admin',
            defaults={
                'email': 'admin@musicblog.com',
                'password': make_password('admin123'),
                'role': admin_role
            }
        )
        self.stdout.write('✓ Создан администратор: admin / admin123')
        
        # Получаем жанры
        phonk = Genre.objects.get(name='Phonk')
        house = Genre.objects.get(name='House')
        techno = Genre.objects.get(name='Techno')
        hiphop = Genre.objects.get(name='Hip-Hop')
        
        # Создаем треки
        tracks_data = [
            {'title': 'Midnight Drive', 'author': 'Electro Wave', 'genre': phonk, 
             'desc': 'Атмосферный трек для ночных поездок. Глубокие басы и мечтательные синтезаторы.'},
            {'title': 'Neon Lights', 'author': 'Synth City', 'genre': house, 
             'desc': 'Энергичный трек с яркими мелодиями и танцевальным ритмом.'},
            {'title': 'Deep Space', 'author': 'Cosmic Beats', 'genre': techno, 
             'desc': 'Космическое путешествие через звуки техно. Минималистичные ритмы.'},
            {'title': 'Urban Flow', 'author': 'City Rhythms', 'genre': hiphop, 
             'desc': 'Уличные ритмы и плавные биты. Рассказ о городской жизни.'},
            {'title': 'Echo Chamber', 'author': 'Deep Mind', 'genre': phonk, 
             'desc': 'Психоделический фонк с необычными звуковыми эффектами.'},
            {'title': 'Sunset Vibes', 'author': 'Beach House', 'genre': house, 
             'desc': 'Расслабляющий хаус для заката на пляже.'},
        ]
        
        for track_data in tracks_data:
            track, created = Track.objects.get_or_create(
                title=track_data['title'],
                defaults={
                    'author_name': track_data['author'],
                    'description': track_data['desc'],
                    'user': test_user,
                    'genre': track_data['genre'],
                    'date_publication': datetime.now().date()
                }
            )
            if created:
                self.stdout.write(f'  - Создан трек: {track.title}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ База данных успешно заполнена!'))