import os
import shutil

from django.conf import settings
from django.db import migrations


# Image files come from tracked static/images/ sources and are copied into
# MEDIA_ROOT/hero_slides/. `manage.py restore_media` re-creates them on any
# environment whose filesystem is missing them (the DB is shared).
SLIDES = [
    {
        'tab_label': 'Overview', 'tab_icon': 'fas fa-bolt', 'accent': 'blue',
        'eyebrow': 'Trusted IT Solutions Since 1985',
        'title': 'Smart IT Solutions for', 'highlight': 'Modern Businesses',
        'subtitle': 'Cloud, Security, Networking & Infrastructure — built around your business.',
        'primary_label': 'Explore Our Services', 'primary_url': '/services/',
        'secondary_label': 'Get Free Consultation', 'secondary_url': '/contact/',
        'image': ('general', 'connected-city.jpg'),
    },
    {
        'tab_label': 'Cloud', 'tab_icon': 'fas fa-cloud', 'accent': 'blue',
        'eyebrow': 'Cloud Solutions',
        'title': 'Move to the Cloud with', 'highlight': 'Zero Disruption',
        'subtitle': 'Strategy, migration and managed operations across AWS, Azure and Microsoft 365 — engineered for uptime.',
        'primary_label': 'Explore Cloud Solutions', 'primary_url': '/services/cloud-solutions/',
        'secondary_label': 'Talk to an Expert', 'secondary_url': '/contact/',
        'image': None,
    },
    {
        'tab_label': 'Security', 'tab_icon': 'fas fa-shield-halved', 'accent': 'green',
        'eyebrow': 'Network & Security',
        'title': 'Security That Stays', 'highlight': 'One Step Ahead',
        'subtitle': 'Next-generation firewalls, secure remote access and managed SOC services that protect your digital assets.',
        'primary_label': 'Explore Network & Security', 'primary_url': '/services/network-security/',
        'secondary_label': 'Talk to an Expert', 'secondary_url': '/contact/',
        'image': ('general', 'tech-team.jpg'),
    },
    {
        'tab_label': 'Infrastructure', 'tab_icon': 'fas fa-server', 'accent': 'orange',
        'eyebrow': 'Remote Infrastructure Management',
        'title': 'Infrastructure Managed', 'highlight': 'Around the Clock',
        'subtitle': '24/7 monitoring, proactive incident management and remote administration that keep your business running.',
        'primary_label': 'Explore Infrastructure Services', 'primary_url': '/services/remote-infrastructure-management/',
        'secondary_label': 'Talk to an Expert', 'secondary_url': '/contact/',
        'image': ('general', 'cyber-security-concept.jpg'),
    },
]


def seed(apps, schema_editor):
    HeroSlide = apps.get_model('core', 'HeroSlide')
    if HeroSlide.objects.exists():
        return
    for order, data in enumerate(SLIDES, start=1):
        data = dict(data)
        image = data.pop('image')
        image_name = ''
        if image:
            src = os.path.join(settings.BASE_DIR, 'static', 'images', *image)
            image_name = f'hero_slides/{image[1]}'
            target = os.path.join(settings.MEDIA_ROOT, image_name)
            if os.path.exists(src) and not os.path.exists(target):
                os.makedirs(os.path.dirname(target), exist_ok=True)
                shutil.copyfile(src, target)
        HeroSlide.objects.create(display_order=order, image=image_name, **data)


def unseed(apps, schema_editor):
    # No-op: slides may have been edited in the dashboard since this ran.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_heroslide'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
