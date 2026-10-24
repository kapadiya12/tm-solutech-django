"""Divyesh Doshi's professional photo (supplied Oct 2026). Replaces only the old placeholder image."""
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import migrations


def set_photo(apps, schema_editor):
    leader = apps.get_model('core', 'Leadership').objects.filter(name='Divyesh Doshi').first()
    src = os.path.join(settings.BASE_DIR, 'static', 'images', 'leadership', 'divyesh-doshi.jpg')
    if not leader or not os.path.exists(src):
        return
    current = os.path.basename(leader.photo.name or '')
    if current and not current.startswith(('team1', 'divyesh-doshi')):
        return   # a different photo was uploaded from the dashboard
    with open(src, 'rb') as f:
        leader.photo.save('divyesh-doshi-2026.jpg', ContentFile(f.read()), save=False)
    leader.save(update_fields=['photo'])


class Migration(migrations.Migration):
    dependencies = [('core', '0017_seed_partners_certs_leadership')]
    operations = [migrations.RunPython(set_photo, migrations.RunPython.noop)]
