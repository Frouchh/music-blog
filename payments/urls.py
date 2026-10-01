from django.urls import path

from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('webhook/', views.yookassa_webhook, name='yookassa_webhook'),
    path('result/<int:order_id>/', views.payment_result, name='payment_result'),
    path('test/<str:external_id>/', views.test_payment, name='test_payment'),
]
