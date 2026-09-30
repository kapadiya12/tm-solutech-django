import os

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from core.models import ClientLogo, HeroSlide, Leadership, SiteSettings
from insights.models import BlogPost
from services.models import Service


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
        "from tracked static/ sources into whatever MEDIA storage backend is "
        "currently configured (local disk, or Cloudinary when CLOUDINARY_URL is "
        "set), wherever the file is missing there — regardless of whether the "
        "database already has the field set. Unlike a migration, this is safe to "
        "re-run on any environment at any time: it checks the storage backend's "
        "actual state, not migration history, which matters when the database is "
        "shared across environments but each environment's disk isn't."
    )

    def handle(self, *args, **options):
        written, skipped, missing_src = 0, 0, 0

        def static_path(*parts):
            return os.path.join(settings.BASE_DIR, 'static', 'images', *parts)

        def ensure(field, src_path, upload_to):
            nonlocal written, skipped, missing_src
            if not os.path.exists(src_path):
                self.stdout.write(self.style.WARNING(f"  source missing, skipped: {src_path}"))
                missing_src += 1
                return

            target_name = field.name or f"{upload_to}/{os.path.basename(src_path)}"
            if field.storage.exists(target_name):
                skipped += 1
                return

            with open(src_path, 'rb') as f:
                saved_name = field.storage.save(target_name, File(f))

            # Some backends (e.g. Cloudinary) silently rename on save even
            # when the requested name didn't already exist, so always sync
            # the DB to whatever name was actually used — never assume the
            # request was honored exactly.
            if saved_name != field.name:
                field.name = saved_name
                field.instance.save(update_fields=[field.field.name])

            written += 1
            self.stdout.write(f"  wrote {saved_name}")

        self.stdout.write("Leadership photos:")
        for name, filename in LEADERSHIP_PHOTOS:
            leader = Leadership.objects.filter(name=name).first()
            if leader:
                ensure(leader.photo, static_path('leadership', filename), 'leadership')

        self.stdout.write("Blog featured images:")
        for slug, filename in BLOG_IMAGES:
            post = BlogPost.objects.filter(slug=slug).first()
            if post:
                ensure(post.featured_image, static_path('blog', filename), 'blog')

        self.stdout.write("Client logos:")
        for i, filename in enumerate(CLIENT_LOGOS, start=1):
            logo = ClientLogo.objects.filter(display_order=i).first()
            if logo:
                ensure(logo.logo, static_path('clients', filename), 'clients')

        # Seeded from any file with the same name under static/images/
        index = {}
        for dirpath, _dirs, files in os.walk(os.path.join(settings.BASE_DIR, 'static', 'images')):
            for filename in files:
                index.setdefault(filename, os.path.join(dirpath, filename))

        self.stdout.write("Hero slide backgrounds:")
        for slide in HeroSlide.objects.exclude(image=''):
            src = index.get(os.path.basename(slide.image.name))
            if src:
                ensure(slide.image, src, 'hero_slides')

        self.stdout.write("Service images:")
        for service in Service.objects.exclude(image=''):
            src = index.get(os.path.basename(service.image.name))
            if src:
                ensure(service.image, src, 'services')

        self.stdout.write("Site logo & favicon:")
        site = SiteSettings.objects.first()
        if site and site.logo:
            ensure(site.logo, static_path('logo', 'tm-solutech-logo.png'), 'settings')
        if site and site.favicon:
            ensure(site.favicon, static_path('logo', 'favicon.png'), 'settings')

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {written} file(s) written, {skipped} already present, {missing_src} source(s) missing."
        ))
