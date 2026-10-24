"""Banner photos (Unsplash License) for the top of each page; only created when missing."""
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import migrations

PAGES = ['contact', 'why-us', 'about', 'leadership', 'clients', 'industries', 'faqs', 'insights', 'work',
         'careers', 'life-at-tm-solutech', 'default']
BADGES = {
    'contact': ('Replies in 1–2 business days', 'Ahmedabad · since 1985'),
    'careers': ('Grow with us', '250+ team members'),
    'life-at-tm-solutech': ('250+ team members', 'Growing together'),
    'clients': ('150+ organisations served', 'Trusted since 1985'),
    'industries': ('6 industries', 'Regulation-ready IT'),
    'faqs': ('Answers in seconds', 'Or ask our team'),
    'insights': ('Expert guides', 'Cloud · Security · AI'),
    'work': ('Real projects', 'Measurable results'),
}


def seed(apps, schema_editor):
    PageBanner = apps.get_model('core', 'PageBanner')
    for page in PAGES:
        if PageBanner.objects.filter(page=page).exists():
            continue
        src = os.path.join(settings.BASE_DIR, 'static', 'images', 'banners', f'{page}.jpg')
        if not os.path.exists(src):
            continue
        b1, b2 = BADGES.get(page, ('35+ years of heritage', 'ISO 9001 · ISO 27000'))
        banner = PageBanner(page=page, badge_1=b1, badge_2=b2)
        with open(src, 'rb') as f:
            banner.image.save(f'{page}.jpg', ContentFile(f.read()), save=False)
        banner.save()


class Migration(migrations.Migration):
    dependencies = [('core', '0019_page_banners')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
