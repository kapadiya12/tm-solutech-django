from django.db import migrations


def seed(apps, schema_editor):
    SocialLink = apps.get_model('core', 'SocialLink')
    SiteSettings = apps.get_model('core', 'SiteSettings')
    if SocialLink.objects.exists():
        return
    s = SiteSettings.objects.filter(pk=1).first()
    if not s:
        return
    rows = [
        ('linkedin', s.linkedin_url),
        ('facebook', s.facebook_url),
        ('instagram', s.instagram_url),
        ('youtube', s.youtube_url),
    ]
    if s.whatsapp_number:
        digits = ''.join(ch for ch in s.whatsapp_number if ch.isdigit())
        if digits:
            rows.append(('whatsapp', f'https://wa.me/{digits}'))
    order = 1
    for platform, url in rows:
        if url:
            SocialLink.objects.create(platform=platform, url=url, display_order=order)
            order += 1


class Migration(migrations.Migration):
    dependencies = [('core', '0009_sociallink')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
