from django.urls import path

from . import views

urlpatterns = [
    path('', views.payouts, name='payouts'),
    path('details/', views.update_details, name='update_details'),
    path('admin/', views.payouts_admin, name='payouts_admin'),
    path('admin/<int:pk>/<str:action>/', views.process_payout, name='process_payout'),
]
