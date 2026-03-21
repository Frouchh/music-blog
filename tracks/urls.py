from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('tracks/', views.tracks_list, name='tracks_list'),
    path('tracks/new/', views.tracks_new, name='tracks_new'),
    path('tracks/week/', views.tracks_week, name='tracks_week'),
    path('track/<int:track_id>/', views.track_detail, name='track_detail'),
    path('upload/', views.upload_track, name='upload_track'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('rate/<int:track_id>/', views.rate_track, name='rate_track'),
    path('moderation/', views.admin_tracks, name='admin_tracks'),  # <--- ИЗМЕНЕНО
    path('moderate/<int:track_id>/<str:action>/', views.moderate_track, name='moderate_track'),
]