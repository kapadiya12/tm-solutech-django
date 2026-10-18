"""Official TM Solutech profiles (LinkedIn, Instagram, Facebook).

Updates the link if the platform already exists, otherwise creates it, and
makes sure each is live in the footer and on the Contact page. Other
platforms added in the dashboard are left untouched.
"""
from django.db import migrations

OFFICIAL = [
    ('linkedin', 'https://www.linkedin.com/company/tmsolutech/'),
    ('instagram', 'https://www.instagram.com/tmsolutech/'),
    ('facebook', 'https://www.facebook.com/tmsolutech/'),
]


def apply(apps, schema_editor):
    SocialLink = apps.get_model('core', 'SocialLink')
    for order, (platform, url) in enumerate(OFFICIAL, start=1):
        link = SocialLink.objects.filter(platform=platform).order_by('display_order', 'id').first()
        if link is None:
            link = SocialLink(platform=platform)
        link.url = url
        link.is_active = True
        link.show_in_footer = True
        link.show_on_contact = True
        link.display_order = order
        link.save()


class Migration(migrations.Migration):
    dependencies = [('core', '0010_seed_social_links')]
    operations = [migrations.RunPython(apply, migrations.RunPython.noop)]
