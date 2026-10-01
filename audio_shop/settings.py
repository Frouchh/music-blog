import os
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Приложения проекта
    'accounts',
    'catalog',
    'orders',
    'payments',
    'downloads',
    'royalties',
    'moderation',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'audio_shop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'orders.context_processors.cart',
            ],
        },
    },
]

WSGI_APPLICATION = 'audio_shop.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'audio_shop'),
        'USER': os.environ.get('DB_USER', 'shop_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}
# Для быстрого запуска без MySQL: DB_ENGINE=sqlite в файле .env
if os.environ.get('DB_ENGINE') == 'sqlite':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'catalog'
LOGOUT_REDIRECT_URL = 'catalog'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Irkutsk'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Публичные файлы: обложки и демонстрационные фрагменты
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Полные аудиофайлы хранятся вне MEDIA_ROOT и отдаются только по ссылке
PROTECTED_MEDIA_ROOT = BASE_DIR / 'protected_media'

# Ограничения по ТЗ
MAX_AUDIO_SIZE = 50 * 1024 * 1024          # 50 МБ
ALLOWED_AUDIO_EXT = ['mp3', 'wav']
PREVIEW_SECONDS = 30                       # длина демофрагмента
SESSION_COOKIE_AGE = 30 * 60               # время жизни сессии 30 минут
SESSION_SAVE_EVERY_REQUEST = True
DOWNLOAD_LINK_TTL = 24 * 60 * 60           # ссылка действует 24 часа
DOWNLOAD_LIMIT = 3                         # не более 3 скачиваний
PLATFORM_FEE = Decimal('0.10')             # комиссия площадки 10 %

# Платёжный шлюз ЮKassa (тестовый магазин).
# Если ключи не заданы, используется встроенная тестовая форма оплаты.
YOOKASSA_SHOP_ID = os.environ.get('YOOKASSA_SHOP_ID')
YOOKASSA_SECRET_KEY = os.environ.get('YOOKASSA_SECRET_KEY')

# Почта: письмо покупателю после оплаты. Без SMTP письма выводятся в консоль.
SITE_URL = os.environ.get('SITE_URL', 'http://127.0.0.1:8000')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'shop@audio-content.local')
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '465'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_SSL = True
EMAIL_BACKEND = ('django.core.mail.backends.smtp.EmailBackend' if EMAIL_HOST
                 else 'django.core.mail.backends.console.EmailBackend')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
