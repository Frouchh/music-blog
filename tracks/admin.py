from django.contrib import admin
from .models import Role, User, Genre, Track, Rating
from django.contrib.auth.hashers import make_password

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['role_id', 'name']
    list_display_links = ['role_id', 'name']
    search_fields = ['name']
    list_per_page = 20


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'login', 'email', 'role']  # Убрал created_at
    list_display_links = ['user_id', 'login']
    list_filter = ['role']
    search_fields = ['login', 'email']
    list_per_page = 20
    readonly_fields = ['user_id']  # Убрал created_at
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user_id', 'login', 'email', 'role')
        }),
        ('Безопасность', {
            'fields': ('password',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data and obj.password:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['user_id']
        return self.readonly_fields


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['genre_id', 'name']
    list_display_links = ['genre_id', 'name']
    search_fields = ['name']
    list_per_page = 20
    ordering = ['name']


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['track_id', 'title', 'author_name', 'user', 'genre', 'status', 'date_publication', 'rating_display']
    list_display_links = ['track_id', 'title']
    list_filter = ['status', 'genre', 'date_publication']
    search_fields = ['title', 'author_name']
    list_per_page = 20
    list_editable = ['status']
    readonly_fields = ['track_id', 'date_publication', 'moderated_at', 'moderated_by']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('track_id', 'title', 'author_name', 'description', 'genre')
        }),
        ('Автор и статус', {
            'fields': ('user', 'status'),
        }),
        ('Аудиофайл', {
            'fields': ('audio_file',),
            'classes': ('collapse',)
        }),
        ('Модерация', {
            'fields': ('moderation_comment', 'moderated_at', 'moderated_by'),
            'classes': ('collapse',)
        }),
        ('Дата', {
            'fields': ('date_publication',),
            'classes': ('collapse',)
        }),
    )
    
    def rating_display(self, obj):
        ratings = obj.rating_set.all()
        if ratings:
            avg = sum(r.score_value for r in ratings) / len(ratings)
            return f"{avg:.1f} ★ ({len(ratings)} оценок)"
        return "Нет оценок"
    rating_display.short_description = 'Рейтинг'
    
    actions = ['approve_tracks', 'reject_tracks']
    
    def approve_tracks(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} треков одобрено')
    approve_tracks.short_description = 'Одобрить выбранные треки'
    
    def reject_tracks(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} треков отклонено')
    reject_tracks.short_description = 'Отклонить выбранные треки'


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['score_id', 'score_value', 'user', 'track']
    list_display_links = ['score_id']
    list_filter = ['score_value']
    search_fields = ['user__login', 'track__title']
    list_per_page = 20
    readonly_fields = ['score_id']


# Настройка заголовка админ-панели
admin.site.site_header = 'Музыкальный блог - Админ-панель'
admin.site.site_title = 'Музыкальный блог'
admin.site.index_title = 'Добро пожаловать в админ-панель'