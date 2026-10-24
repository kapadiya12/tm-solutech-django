"""
Client-supplied content (Oct 2026): technology partners, certifications and
leadership titles/LinkedIn links.

- Partners and certifications are only created when missing (matched by name).
- Partner logos come from tracked files in static/images/partners/.
"""
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import migrations

PARTNERS = [
    # name, logo file, category
    ('Microsoft', 'microsoft.svg', 'software'),
    ('Adobe', 'adobe.svg', 'software'),
    ('Oracle', 'oracle.svg', 'software'),
    ('Check Point', 'checkpoint.svg', 'security'),
    ('WatchGuard', 'watchguard.svg', 'security'),
    ('AWS', 'aws.svg', 'software'),
    ('Google', 'google.svg', 'software'),
    ('Corel', 'corel.svg', 'software'),
    ('Cisco', 'cisco.svg', 'networking'),
    ('HPE', 'hpe.svg', 'hardware'),
    ('Lenovo', 'lenovo.svg', 'hardware'),
    ('IBM', 'ibm.svg', 'hardware'),
    ('Dell', 'dell.svg', 'hardware'),
    ('Samsung', 'samsung.svg', 'hardware'),
    ('Asus', 'asus.svg', 'hardware'),
    ('Acer', 'acer.svg', 'hardware'),
    ('Canon', 'canon.svg', 'hardware'),
    ('CP Plus', 'cpplus.svg', 'networking'),
    ('Netgear', 'netgear.svg', 'networking'),
]

CERTIFICATIONS = [
    ('ISO 9001', 'Quality Management System', 'Certified processes for consistent, high-quality delivery and continual improvement.', 'fas fa-award'),
    ('ISO 27000', 'Information Security Management', 'Certified practices for protecting information, systems and client data.', 'fas fa-shield-halved'),
]

LEADERSHIP = {
    'Saumil Shah': 'https://www.linkedin.com/in/saumil-shah-898598a/',
    'Binit Shah': 'https://www.linkedin.com/in/binit-shah-9a63113/',
    'Saurin Shah': 'https://www.linkedin.com/in/saurin-shah-253230196/',
    'Divyesh Doshi': 'https://www.linkedin.com/in/divyeshdoshi/',
    'Maunish Shah': 'https://www.linkedin.com/in/maunish-shah-87a1aa14/',
}
SAURIN_BIO = ('With 28+ years of experience in IT infrastructure and enterprise IT solutions, Saurin helps clients '
              'design, optimise and modernise their IT infrastructure.')


def seed(apps, schema_editor):
    Partner = apps.get_model('core', 'Partner')
    Certification = apps.get_model('core', 'Certification')
    Leadership = apps.get_model('core', 'Leadership')

    for order, (name, filename, category) in enumerate(PARTNERS, start=1):
        if Partner.objects.filter(name__iexact=name).exists():
            continue
        partner = Partner(name=name, category=category, display_order=order)
        src = os.path.join(settings.BASE_DIR, 'static', 'images', 'partners', filename)
        if os.path.exists(src):
            with open(src, 'rb') as f:
                partner.logo.save(filename, ContentFile(f.read()), save=False)
        partner.save()

    for order, (name, title, desc, icon) in enumerate(CERTIFICATIONS, start=1):
        Certification.objects.get_or_create(name=name, defaults={
            'title': title, 'description': desc, 'icon': icon, 'display_order': order})

    for order, (name, url) in enumerate(LEADERSHIP.items(), start=1):
        leader = Leadership.objects.filter(name=name).first()
        if not leader:
            continue
        leader.designation = 'Co-Founder & Director'
        leader.linkedin_url = url
        leader.display_order = order
        fields = ['designation', 'linkedin_url', 'display_order']
        if name == 'Saurin Shah':
            leader.short_bio = SAURIN_BIO
            fields.append('short_bio')
        leader.save(update_fields=fields)


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0016_partners_certifications'),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
