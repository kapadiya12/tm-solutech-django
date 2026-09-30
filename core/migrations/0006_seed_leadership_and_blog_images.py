import os
import shutil

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import migrations


# (Leadership.name, source file under static/images/leadership/)
LEADERSHIP_PHOTOS = [
    ('Saumil Shah', 'saumil-shah.jpg'),
    ('Binit Shah', 'binit-shah.jpg'),
    ('Saurin Shah', 'saurin-shah.jpg'),
    ('Maunish Shah', 'maunish-shah.jpg'),
    ('Divyesh Doshi', 'divyesh-doshi.jpg'),
]

# (BlogPost.slug, source file under static/images/blog/)
BLOG_IMAGES = [
    ('custom-copilot-transforming-medical-rep-conversations', 'custom-copilot.jpg'),
    ('ensuring-compliance-sebi-cybersecurity-framework-managed-soc', 'managed-soc.jpg'),
    ('understanding-cscrf-compliance-sebi-regulated-entities', 'cscrf-compliance.png'),
]


def _static_path(*parts):
    return os.path.join(settings.BASE_DIR, 'static', 'images', *parts)


def _ensure_file(field, src_path):
    """
    Get this environment's copy of the media file in sync with what the
    (possibly shared, cross-environment) database row already expects.

    Two cases:
    - The field already has a filename (common: this is a shared production
      DB that already has the right value, but *this* filesystem — e.g. a
      fresh Render deploy — never received the actual file bytes). Write the
      source image straight to that exact MEDIA_ROOT path so it lines up
      with the existing DB value, without touching the DB at all.
    - The field is empty (a genuinely fresh database). Use .save() so both
      the DB value and the file are set together.
    """
    if not os.path.exists(src_path):
        return

    if field.name:
        target_path = os.path.join(settings.MEDIA_ROOT, field.name)
        if os.path.exists(target_path):
            return
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        shutil.copyfile(src_path, target_path)
    else:
        with open(src_path, 'rb') as f:
            field.save(os.path.basename(src_path), ContentFile(f.read()), save=True)


def seed(apps, schema_editor):
    Leadership = apps.get_model('core', 'Leadership')
    BlogPost = apps.get_model('insights', 'BlogPost')

    for name, filename in LEADERSHIP_PHOTOS:
        leader = Leadership.objects.filter(name=name).first()
        if not leader:
            continue
        _ensure_file(leader.photo, _static_path('leadership', filename))

    for slug, filename in BLOG_IMAGES:
        post = BlogPost.objects.filter(slug=slug).first()
        if not post:
            continue
        _ensure_file(post.featured_image, _static_path('blog', filename))


def unseed(apps, schema_editor):
    # Intentionally a no-op: reversing would delete photos that may have been
    # replaced or re-uploaded from the dashboard since this migration ran.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_seed_homepage_content'),
        ('insights', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
