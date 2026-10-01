from django.db import migrations

ROLES = [('buyer', 'Покупатель'), ('author', 'Автор'), ('admin', 'Администратор')]
STATUSES = ['На модерации', 'Опубликован', 'Отклонён', 'Снят с продажи']
GENRES = ['Электроника', 'Хип-хоп', 'Phonk', 'House', 'Techno', 'Lo-fi', 'Рок', 'Эмбиент']
LICENSES = [
    ('Личная', 'Прослушивание, без коммерческого использования. Формат MP3.', False),
    ('Коммерческая', 'Использование в видео, рекламе, подкастах. Форматы MP3 и WAV.', False),
    ('Эксклюзивная', 'Полные права, трек снимается с продажи. Формат WAV.', True),
]


def load(apps, schema_editor):
    Role = apps.get_model('accounts', 'Role')
    for name, title in ROLES:
        Role.objects.get_or_create(name=name, defaults={'title': title})
    Status = apps.get_model('catalog', 'Status')
    for name in STATUSES:
        Status.objects.get_or_create(name=name)
    Genre = apps.get_model('catalog', 'Genre')
    for name in GENRES:
        Genre.objects.get_or_create(name=name)
    LicenseType = apps.get_model('catalog', 'LicenseType')
    for name, description, exclusive in LICENSES:
        LicenseType.objects.get_or_create(
            name=name, defaults={'description': description, 'is_exclusive': exclusive})


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('catalog', '0001_initial'),
    ]

    operations = [migrations.RunPython(load, migrations.RunPython.noop)]
