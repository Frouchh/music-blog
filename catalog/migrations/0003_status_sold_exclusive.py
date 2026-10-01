from django.db import migrations


def add_status(apps, schema_editor):
    Status = apps.get_model('catalog', 'Status')
    Status.objects.get_or_create(name='Продан эксклюзивно')


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_initial_data'),
    ]

    operations = [migrations.RunPython(add_status, migrations.RunPython.noop)]
