"""Industry images from the previous tmsolutech.com site (tracked in static/images/industries/).
Only fills industries that don't have an image yet."""
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import migrations

IMAGES = {'hi-tech': 'hi-tech.png', 'banking': 'banking.png', 'medical': 'medical.jpg',
          'industrial': 'industrial.png', 'sme': 'sme.jpg'}


def seed(apps, schema_editor):
    Industry = apps.get_model('services', 'Industry')
    for slug, filename in IMAGES.items():
        industry = Industry.objects.filter(slug=slug).first()
        src = os.path.join(settings.BASE_DIR, 'static', 'images', 'industries', filename)
        if not industry or industry.image or not os.path.exists(src):
            continue
        with open(src, 'rb') as f:
            industry.image.save(filename, ContentFile(f.read()), save=False)
        industry.save(update_fields=['image'])


class Migration(migrations.Migration):
    dependencies = [
        ('services', '0005_client_service_catalog'),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
