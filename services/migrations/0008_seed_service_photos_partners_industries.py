"""
Service page content refresh (Oct 2026).

- Topic photos (Unsplash License) for every service and service area, from
  static/images/services/ and static/images/service-categories/. A service's
  image is only replaced while it is empty or still one of the old shared
  placeholder images; anything uploaded from the dashboard is kept.
- Technology partners for each service area (only when none are set).
- Industries updated to the client's list. Slugs are kept so existing links
  keep working; Medical & Pharmaceuticals is hidden (not deleted).
"""
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import migrations

OLD_PLACEHOLDERS = ('microsoft-365', 'cyber-security-concept', 'connected-city', 'tech-team',
                    'quality-control', 'about_composite')

CATEGORY_PARTNERS = {
    'ai-modernization': ['Microsoft', 'Google', 'AWS', 'Oracle', 'IBM'],
    'cloud-solutions': ['Microsoft', 'AWS', 'Google', 'Oracle'],
    'cybersecurity-excellence': ['Check Point', 'WatchGuard', 'Microsoft', 'Cisco'],
    'network-security': ['Cisco', 'Check Point', 'WatchGuard', 'HPE', 'Netgear', 'CP Plus'],
    'remote-infrastructure-management': ['Microsoft', 'HPE', 'Dell', 'IBM', 'Cisco'],
    'it-hardware-var': ['Dell', 'HPE', 'Lenovo', 'Asus', 'Acer', 'Samsung', 'Canon', 'Microsoft', 'Adobe', 'Corel'],
}

# slug: (name, icon, short description, display order) – applied only while the old default name is unchanged
INDUSTRIES = {
    'industrial': ('Industrial & Manufacturing', 'Large Enterprise – Manufacturing', 'fas fa-industry',
                   'ERP and SAP infrastructure, plant and office networks, data centre and end-user computing for large manufacturing enterprises.', 1),
    'education': (None, 'Education', 'fas fa-graduation-cap',
                  'Campus networks and Wi-Fi, computer labs, secure collaboration and IT support for schools, colleges and universities.', 2),
    'sme': ('Small & Medium Enterprises', 'SMB', 'fas fa-briefcase',
            'End-to-end IT for small and medium businesses: modern infrastructure, managed security and support that grows with you.', 3),
    'banking': ('Banking & Financial Services', 'BFSI', 'fas fa-building-columns',
                'Banking, financial services and insurance: core banking security, SEBI CSCRF compliance, managed SOC and solutions trusted by 150+ banks.', 4),
    'hi-tech': ('Hi-Tech', 'Software Development', 'fas fa-code',
                'Development and test environments, cloud and DevOps-ready infrastructure, licensing and secure networks for software companies.', 5),
}


def _static(*parts):
    return os.path.join(settings.BASE_DIR, 'static', 'images', *parts)


def _put(field, src, filename):
    with open(src, 'rb') as f:
        field.save(filename, ContentFile(f.read()), save=False)


def seed(apps, schema_editor):
    Service = apps.get_model('services', 'Service')
    ServiceCategory = apps.get_model('services', 'ServiceCategory')
    Industry = apps.get_model('services', 'Industry')
    Partner = apps.get_model('core', 'Partner')

    for service in Service.objects.all():
        src = _static('services', f'{service.slug}.jpg')
        if not os.path.exists(src):
            continue
        current = os.path.splitext(os.path.basename(service.image.name or ''))[0]
        if current and not current.startswith(OLD_PLACEHOLDERS):
            continue
        _put(service.image, src, f'{service.slug}.jpg')
        service.save(update_fields=['image'])

    partners = {p.name: p for p in Partner.objects.all()}
    for category in ServiceCategory.objects.all():
        src = _static('service-categories', f'{category.slug}.jpg')
        if not category.image and os.path.exists(src):
            _put(category.image, src, f'{category.slug}.jpg')
            category.save(update_fields=['image'])
        if not category.partners.exists():
            category.partners.set([partners[n] for n in CATEGORY_PARTNERS.get(category.slug, []) if n in partners])

    for slug, (old_name, name, icon, short, order) in INDUSTRIES.items():
        industry = Industry.objects.filter(slug=slug).first()
        if industry is None:
            industry = Industry(slug=slug, name=name, icon=icon, short_description=short, display_order=order, is_active=True)
            src = _static('industries', f'{slug}.jpg')
            if os.path.exists(src):
                _put(industry.image, src, f'{slug}.jpg')
            industry.save()
            continue
        if old_name and industry.name == old_name:
            industry.name, industry.icon, industry.short_description = name, icon, short
            industry.display_order = order
            industry.save(update_fields=['name', 'icon', 'short_description', 'display_order'])
    Industry.objects.filter(slug='medical', name='Medical & Pharmaceuticals').update(is_active=False)


class Migration(migrations.Migration):
    dependencies = [
        ('services', '0007_servicepagesettings_service_hero_stats_and_more'),
        ('core', '0017_seed_partners_certs_leadership'),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
