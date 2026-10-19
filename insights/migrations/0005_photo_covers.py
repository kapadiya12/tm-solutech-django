"""
Swap placeholder covers for photos (Unsplash License) on the launch articles.
Only covers that are still the original placeholder files are replaced, so an
image uploaded from the dashboard is never touched.
"""
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import migrations

# slug: (placeholder file prefixes, new photo under static/images/blog/)
COVERS = {
    'understanding-cscrf-compliance-sebi-regulated-entities': (('cscrf-compliance',), 'cscrf-trading.jpg'),
    'cloud-migration-checklist-for-growing-businesses': (('cloud-migration-checklist',), 'cloud-migration.jpg'),
    'vapt-explained-vulnerability-assessment-penetration-testing': (('vapt-explained',), 'vapt.jpg'),
    'disaster-recovery-planning-rto-rpo-backups': (('disaster-recovery-planning',), 'disaster-recovery.jpg'),
}


def swap(apps, schema_editor):
    BlogPost = apps.get_model('insights', 'BlogPost')
    for slug, (old_prefixes, filename) in COVERS.items():
        post = BlogPost.objects.filter(slug=slug).first()
        src = os.path.join(settings.BASE_DIR, 'static', 'images', 'blog', filename)
        if not post or not os.path.exists(src):
            continue
        current = os.path.basename(post.featured_image.name or '')
        if current and not current.startswith(old_prefixes):
            continue
        with open(src, 'rb') as f:
            post.featured_image.save(filename, ContentFile(f.read()), save=False)
        post.save(update_fields=['featured_image'])


class Migration(migrations.Migration):
    dependencies = [
        ('insights', '0004_seed_full_articles'),
    ]

    operations = [
        migrations.RunPython(swap, migrations.RunPython.noop),
    ]
