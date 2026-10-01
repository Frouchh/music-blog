from django.urls import path

from . import views

urlpatterns = [
    path('', views.queue, name='moderation_queue'),
    path('track/<int:pk>/<str:action>/', views.moderate, name='moderate'),
    path('users/', views.users, name='moderation_users'),
    path('users/<int:pk>/block/', views.toggle_block, name='toggle_block'),
    path('report/', views.report, name='moderation_report'),
]
