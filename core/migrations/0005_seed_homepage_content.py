import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import migrations


CAPABILITIES = [
    {'title': 'Cloud', 'icon': 'fas fa-cloud', 'description': 'Strategy, migration, and managed cloud operations across AWS, Azure, and hybrid environments.', 'display_order': 1},
    {'title': 'Cyber Security', 'icon': 'fas fa-shield-alt', 'description': 'Threat detection, endpoint protection, and compliance-ready security architecture.', 'display_order': 2},
    {'title': 'Networking', 'icon': 'fas fa-network-wired', 'description': 'Enterprise-grade network design, implementation, and 24/7 monitored connectivity.', 'display_order': 3},
    {'title': 'Infrastructure', 'icon': 'fas fa-server', 'description': 'Data center, virtualization, and remote infrastructure management built for uptime.', 'display_order': 4},
    {'title': 'Enterprise IT', 'icon': 'fas fa-building', 'description': 'End-to-end IT operations, support, and lifecycle management tailored to your business.', 'display_order': 5},
]

HERO_TAGS = [
    {'icon': 'fas fa-cloud', 'label': 'Cloud Solutions', 'display_order': 1},
    {'icon': 'fas fa-shield-alt', 'label': 'Cyber Security', 'display_order': 2},
    {'icon': 'fas fa-network-wired', 'label': 'Networking', 'display_order': 3},
    {'icon': 'fas fa-server', 'label': 'Enterprise IT', 'display_order': 4},
]

HERO_STATS = [
    {'icon': 'fas fa-cloud-upload-alt', 'label': 'Cloud Migrations', 'value': 'Seamless', 'display_order': 1},
    {'icon': 'fas fa-shield-alt', 'label': 'Security Level', 'value': 'Enterprise', 'display_order': 2},
    {'icon': 'fas fa-headset', 'label': 'Support', 'value': '24/7', 'display_order': 3},
]

CLIENT_LOGOS = [
    {'name': f'Client {i}', 'file': f'icon{i}.png', 'display_order': i}
    for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
]


def seed(apps, schema_editor):
    Capability = apps.get_model('core', 'Capability')
    HeroTag = apps.get_model('core', 'HeroTag')
    HeroStat = apps.get_model('core', 'HeroStat')
    ClientLogo = apps.get_model('core', 'ClientLogo')

    for row in CAPABILITIES:
        Capability.objects.get_or_create(title=row['title'], defaults=row)
    for row in HERO_TAGS:
        HeroTag.objects.get_or_create(label=row['label'], defaults=row)
    for row in HERO_STATS:
        HeroStat.objects.get_or_create(label=row['label'], defaults=row)

    static_clients_dir = os.path.join(settings.BASE_DIR, 'static', 'images', 'clients')
    for row in CLIENT_LOGOS:
        if ClientLogo.objects.filter(name=row['name']).exists():
            continue
        src_path = os.path.join(static_clients_dir, row['file'])
        if not os.path.exists(src_path):
            continue
        with open(src_path, 'rb') as f:
            content = f.read()
        logo = ClientLogo(name=row['name'], display_order=row['display_order'])
        logo.logo.save(row['file'], ContentFile(content), save=False)
        logo.save()


def unseed(apps, schema_editor):
    Capability = apps.get_model('core', 'Capability')
    HeroTag = apps.get_model('core', 'HeroTag')
    HeroStat = apps.get_model('core', 'HeroStat')
    ClientLogo = apps.get_model('core', 'ClientLogo')
    Capability.objects.filter(title__in=[c['title'] for c in CAPABILITIES]).delete()
    HeroTag.objects.filter(label__in=[t['label'] for t in HERO_TAGS]).delete()
    HeroStat.objects.filter(label__in=[s['label'] for s in HERO_STATS]).delete()
    ClientLogo.objects.filter(name__in=[c['name'] for c in CLIENT_LOGOS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_capability_clientlogo_herostat_herotag'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
