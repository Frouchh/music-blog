from django.db import models
from django.contrib.auth.models import AbstractUser

class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'Roles'
    
    def __str__(self):
        return self.name

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    login = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=100, unique=True)
    role = models.ForeignKey(Role, on_delete=models.RESTRICT, db_column='Role_id')
    
    class Meta:
        db_table = 'Users'
    
    def __str__(self):
        return self.login

class Genre(models.Model):
    genre_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'Genres'
    
    def __str__(self):
        return self.name

class Track(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На модерации'),
        ('approved', 'Одобрен'),
        ('rejected', 'Отклонен'),
    ]
    
    track_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=45)
    author_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date_publication = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='User_id')
    genre = models.ForeignKey(Genre, on_delete=models.RESTRICT, db_column='Genre_id')
    audio_file = models.FileField(upload_to='tracks/', blank=True, null=True, verbose_name='Аудиофайл')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    moderation_comment = models.TextField(blank=True, null=True, verbose_name='Комментарий модератора')
    moderated_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата модерации')
    moderated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_tracks', verbose_name='Модератор')
    
    class Meta:
        db_table = 'Tracks'
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def average_rating(self):
        ratings = self.rating_set.all()
        if ratings:
            return sum(r.score_value for r in ratings) / len(ratings)
        return 0

class Rating(models.Model):
    score_id = models.AutoField(primary_key=True)
    score_value = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='User_id')
    track = models.ForeignKey(Track, on_delete=models.CASCADE, db_column='Track_id')
    
    class Meta:
        db_table = 'Ratings'
        unique_together = ['user', 'track']  # Один пользователь - одна оценка на трек
    
    def __str__(self):
        return f"{self.user.login} - {self.track.title}: {self.score_value}"