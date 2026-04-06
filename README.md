[README.md](https://github.com/user-attachments/files/26186509/README.md)
# 🎵 Музыкальный блог

Веб-приложение для публикации и прослушивания музыки с системой модерации контента.

## 📋 Функционал

- Регистрация и авторизация пользователей
- Прослушивание музыкальных треков (встроенный аудиоплеер)
- Публикация треков с загрузкой аудиофайлов (MP3, WAV)
- Система оценки треков по 10-балльной шкале
- Модерация контента (треки проходят проверку администратором)
- Поиск по названию трека и имени автора
- Фильтрация треков по жанру
- Личный кабинет пользователя с отображением статуса треков
- Страница модерации для администратора

## 🛠 Технологии

- **Backend:** Python 3.12, Django 4.2
- **Database:** MySQL / MariaDB или SQLite
- **Frontend:** HTML5, CSS3, JavaScript
- **Дополнительно:** AJAX (оценка треков без перезагрузки страницы)

## 🚀 Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/Frouchh/music-blog.git
cd music-blog
2. Создание и активация виртуального окружения
Windows:

bash
python -m venv venv
venv\Scripts\activate
Mac/Linux:

bash
python3 -m venv venv
source venv/bin/activate
3. Установка зависимостей
bash
pip install -r requirements.txt
4. Настройка базы данных
Вариант А: SQLite (рекомендуется для быстрого запуска)
Откройте файл music_blog/settings.py

Найдите блок DATABASES и замените его на:

python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
База данных создастся автоматически при миграции

Вариант Б: MySQL (для production)
Убедитесь, что MySQL сервер запущен

Создайте базу данных:

sql
CREATE DATABASE music_blog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
Откройте файл music_blog/settings.py и настройте подключение:

python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'music_blog',
        'USER': 'root',
        'PASSWORD': 'ваш_пароль',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
Если используете XAMPP, пароль по умолчанию пустой: 'PASSWORD': ''

Для работы с MySQL может потребоваться установка драйвера:

bash
pip install mysqlclient
или

bash
pip install pymysql
Если используете pymysql, добавьте в music_blog/__init__.py:

python
import pymysql
pymysql.install_as_MySQLdb()
5. Применение миграций
bash
python manage.py makemigrations
python manage.py migrate
6. Создание суперпользователя (администратора)
bash
python manage.py createsuperuser
Введите:

Username: admin

Email: admin@example.com

Password: admin123

7. Заполнение базы тестовыми данными (опционально)
bash
python fill_db.py
Создаст:

Роли: admin, user, moderator

Жанры: Phonk, House, Techno, Hip-Hop

Тестового пользователя: testuser / test123

Тестовые треки

8. Сбор статических файлов
bash
python manage.py collectstatic --noinput
9. Запуск сервера
bash
python manage.py runserver
Откройте в браузере: http://127.0.0.1:8000/

👥 Учетные записи для тестирования
Роль	        Логин    Пароль
Администратор	adminт   admin123
Пользователь	testuser test123
🔧 Структура проекта
text
music-blog/
├── manage.py                 # Управление проектом
├── requirements.txt          # Зависимости
├── fill_db.py                # Скрипт заполнения тестовыми данными
├── music_blog/               # Настройки проекта
│   ├── settings.py           # Конфигурация Django
│   └── urls.py               # Основные маршруты
├── tracks/                   # Основное приложение
│   ├── models.py             # Модели базы данных
│   ├── views.py              # Представления
│   ├── urls.py               # Маршруты приложения
│   └── migrations/           # Миграции базы данных
├── templates/                # HTML шаблоны
│   ├── base.html             # Базовый шаблон
│   ├── index.html            # Главная страница
│   ├── track.html            # Страница трека
│   ├── upload.html           # Публикация трека
│   ├── profile.html          # Личный кабинет
│   ├── login.html            # Вход
│   ├── register.html         # Регистрация
│   └── admin_tracks.html     # Страница модерации
├── static/                   # CSS, изображения, иконки
└── media/                    # Загруженные аудиофайлы (создаётся автоматически)
