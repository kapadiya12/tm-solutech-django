"""All homepage industries are current: show Medical & Pharmaceuticals again."""
from django.db import migrations


def show(apps, schema_editor):
    apps.get_model('services', 'Industry').objects.filter(slug='medical').update(is_active=True, display_order=6)


class Migration(migrations.Migration):
    dependencies = [('services', '0009_service_page_home_sections')]
    operations = [migrations.RunPython(show, migrations.RunPython.noop)]
