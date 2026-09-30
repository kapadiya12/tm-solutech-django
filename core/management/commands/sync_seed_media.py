import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Leadership, ClientLogo
from insights.models import BlogPost


LEADERSHIP_PHOTOS = [
    ('Saumil Shah', 'saumil-shah.jpg'),
    ('Binit Shah', 'binit-shah.jpg'),
    ('Saurin Shah', 'saurin-shah.jpg'),
    ('Maunish Shah', 'maunish-shah.jpg'),
    ('Divyesh Doshi', 'divyesh-doshi.jpg'),
]

BLOG_IMAGES = [
    ('custom-copilot-transforming-medical-rep-conversations', 'custom-copilot.jpg'),
    ('ensuring-compliance-sebi-cybersecurity-framework-managed-soc', 'managed-soc.jpg'),
    ('understanding-cscrf-compliance-sebi-regulated-entities', 'cscrf-compliance.png'),
]

CLIENT_LOGOS = [f'icon{i}.png' for i in range(1, 15)]


class Command(BaseCommand):
    help = (
        "Copies seed images (leadership photos, blog featured images, client logos) "
        "from tracked static/ sources into MEDIA_ROOT wherever the file is missing "
        "on THIS filesystem, regardless of whether the database already has the "
        "field set. Unlike a migration, this is safe to re-run on any environment "
        "at any time — it checks disk state, not migration history, which matters "
        "when the database is shared across environments (e.g. local + Render) but "
        "each environment's filesystem is separate."
    )

    def handle(self, *args, **options):
        written, skipped, missing_src = 0, 0, 0

        def static_path(*parts):
            return os.path.join(settings.BASE_DIR, 'static', 'images', *parts)

        def ensure(field, src_path):
            nonlocal written, skipped, missing_src
            if not os.path.exists(src_path):
                self.stdout.write(self.style.WARNING(f"  source missing, skipped: {src_path}"))
                missing_src += 1
                return
            if field.name:
                target_path = os.path.join(settings.MEDIA_ROOT, field.name)
                if os.path.exists(target_path):
                    skipped += 1
                    return
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.copyfile(src_path, target_path)
                written += 1
                self.stdout.write(f"  wrote {target_path}")
            else:
                with open(src_path, 'rb') as f:
                    field.save(os.path.basename(src_path), f, save=True)
                written += 1
                self.stdout.write(f"  set + wrote {field.name}")

        self.stdout.write("Leadership photos:")
        for name, filename in LEADERSHIP_PHOTOS:
            leader = Leadership.objects.filter(name=name).first()
            if leader:
                ensure(leader.photo, static_path('leadership', filename))

        self.stdout.write("Blog featured images:")
        for slug, filename in BLOG_IMAGES:
            post = BlogPost.objects.filter(slug=slug).first()
            if post:
                ensure(post.featured_image, static_path('blog', filename))

        self.stdout.write("Client logos:")
        for i, filename in enumerate(CLIENT_LOGOS, start=1):
            logo = ClientLogo.objects.filter(display_order=i).first()
            if logo:
                ensure(logo.logo, static_path('clients', filename))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {written} file(s) written, {skipped} already present, {missing_src} source(s) missing."
        ))
