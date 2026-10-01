from django.urls import path

from . import views

urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('track/<int:pk>/', views.track_detail, name='track_detail'),
    path('track/<int:pk>/review/', views.add_review, name='add_review'),
    path('track/<int:pk>/prices/', views.edit_prices, name='edit_prices'),
    path('album/<int:pk>/', views.album_detail, name='album_detail'),
    path('author/upload/', views.upload_track, name='upload_track'),
    path('author/', views.author_tracks, name='author_tracks'),
]
