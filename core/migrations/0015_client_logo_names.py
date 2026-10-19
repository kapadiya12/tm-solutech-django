"""Real names for the client logos imported from the previous tmsolutech.com site.
A logo is only renamed while it still has its placeholder name ("Client N")."""
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import migrations

NAMES = {
    'icon2': 'The Gujarat State Co-op. Bank',
    'icon3': 'Adarsh Co-operative Bank',
    'icon4': 'Amneal Pharmaceuticals',
    'icon5': 'APCER Life Sciences',
    'icon6': 'Atul Ltd',
    'icon7': 'Bodal Chemicals',
    'icon8': 'Arvind SmartSpaces',
    'icon9': 'CEPT University',
    'icon10': 'MICA',
    'icon11': 'Ashima',
    'icon12': 'Oshwal Education Trust',
    'icon13': 'Radix',
    'icon14': 'Ahmedabad University',
}
# Sharper/wider versions used on the old site
BETTER_FILES = {'icon2': 'icon2-1.png'}


def rename(apps, schema_editor):
    ClientLogo = apps.get_model('core', 'ClientLogo')
    for logo in ClientLogo.objects.all():
        stem = os.path.splitext(os.path.basename(logo.logo.name or ''))[0].split('_')[0]
        if stem not in NAMES or not logo.name.startswith('Client '):
            continue
        logo.name = NAMES[stem]
        fields = ['name']
        better = BETTER_FILES.get(stem)
        src = better and os.path.join(settings.BASE_DIR, 'static', 'images', 'clients', better)
        if src and os.path.exists(src):
            with open(src, 'rb') as f:
                logo.logo.save(better, ContentFile(f.read()), save=False)
            fields.append('logo')
        logo.save(update_fields=fields)


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0014_remove_faq_legacy_category'),
    ]

    operations = [
        migrations.RunPython(rename, migrations.RunPython.noop),
    ]
