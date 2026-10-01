from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('catalog.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('downloads/', include('downloads.urls')),
    path('royalties/', include('royalties.urls')),
    path('moderation/', include('moderation.urls')),
]

# Отдаются только публичные файлы (обложки и демофрагменты).
# Каталог protected_media веб-сервером не публикуется.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
