"""
Facts carried over from the previous tmsolutech.com site that the new site was missing.
Every change only fills an empty field or appends to the original launch text, so
anything edited from the dashboard is kept.
"""
from django.db import migrations

AUTOBANK = ' He also created Autobank, banking software built exclusively for co-operative banks.'
SAURIN_EXTRA = ' His work spans data centre projects and networking for SMEs and corporates, with an emphasis on meticulous planning, execution and long-term client relationships.'
DIVYESH_EXTRA = ' Previously a Project Manager at Jin Shree Computers and founder of Security Exposure, a penetration testing, network auditing and security architecture practice.'
MAUNISH_EXTRA = ' He has also led work for banks and credit societies, and is known for building high-performance teams.'

NEW_REASONS = [
    ('Professional Approach', 'fas fa-briefcase',
     'We are dutiful and committed to the highest quality of products and services, which is why our clients can count on timely delivery and dependable support.'),
    ('Teamwork Is Key', 'fas fa-people-group',
     'An open, inclusive culture that brings together different talents and experiences. We reach the best answers by discussing a range of views, with you and within our team.'),
]
CROSS_INDUSTRY = ('Deep experience across banking, hi-tech, pharmaceuticals, manufacturing, education, agriculture, hospitality, '
                  'construction and SMEs, trusted by organisations such as CEPT University, DDB Mudra Group, Adarsh Co-op. Bank and '
                  'The Gujarat State Co-op. Bank.')


def apply(apps, schema_editor):
    Leadership = apps.get_model('core', 'Leadership')
    WhyUsReason = apps.get_model('core', 'WhyUsReason')
    SocialLink = apps.get_model('core', 'SocialLink')

    for name, extra, marker in [('Saumil Shah', AUTOBANK, 'Autobank'), ('Saurin Shah', SAURIN_EXTRA, 'data centre'),
                                ('Divyesh Doshi', DIVYESH_EXTRA, 'Jin Shree'), ('Maunish Shah', MAUNISH_EXTRA, 'credit societies')]:
        leader = Leadership.objects.filter(name=name).first()
        if leader and marker not in (leader.short_bio or ''):
            leader.short_bio = (leader.short_bio or '').rstrip() + extra
            leader.save(update_fields=['short_bio'])

    reason = WhyUsReason.objects.filter(title='Cross-Industry Expertise').first()
    if reason and reason.description.startswith('Deep experience across Banking, Hi-Tech, Medical'):
        reason.description = CROSS_INDUSTRY
        reason.save(update_fields=['description'])
    last = WhyUsReason.objects.order_by('-display_order').values_list('display_order', flat=True).first() or 0
    for i, (title, icon, desc) in enumerate(NEW_REASONS, start=1):
        WhyUsReason.objects.get_or_create(title=title, defaults={'icon': icon, 'description': desc, 'display_order': last + i, 'is_active': True})

    if not SocialLink.objects.filter(platform='x').exists():
        SocialLink.objects.create(platform='x', url='https://twitter.com/tmsolutech', label='X (Twitter)',
                                  show_in_footer=True, show_on_contact=True, is_active=True, display_order=4)


class Migration(migrations.Migration):
    dependencies = [('core', '0020_seed_page_banners')]
    operations = [migrations.RunPython(apply, migrations.RunPython.noop)]
