import os
import shutil

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from core.models import ClientLogo, HeroSlide, Leadership, SiteSettings
from insights.models import BlogPost
from services.models import Service, ServiceCategory


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


class Command(BaseCommand):
    help = (
        "Restore missing seeded media files (leadership photos, blog images, "
        "site logo, client logos) from their tracked copies in static/images/. "
        "The database is shared across environments but media/ is not in git, "
        "so rows can point at files that don't exist on this machine. Safe to "
        "run on every deploy: existing files and DB values are never changed."
    )

    def handle(self, *args, **options):
        self.restored = 0

        for name, filename in LEADERSHIP_PHOTOS:
            leader = Leadership.objects.filter(name=name).first()
            if leader:
                self._ensure_file(leader, 'photo', _static_path('leadership', filename))

        for slug, filename in BLOG_IMAGES:
            post = BlogPost.objects.filter(slug=slug).first()
            if post:
                self._ensure_file(post, 'featured_image', _static_path('blog', filename))

        site = SiteSettings.objects.first()
        if site and site.logo:
            self._ensure_file(site, 'logo', _static_path('logo', 'tm-solutech-logo.png'))
        if site and site.favicon:
            self._ensure_file(site, 'favicon', _static_path('logo', 'favicon.png'))

        # Client logos were seeded as clients/iconN.png from static/images/clients/
        for client in ClientLogo.objects.exclude(logo=''):
            self._ensure_file(client, 'logo', _static_path('clients', os.path.basename(client.logo.name)))

        # Anything else seeded from static/images/ (hero slides, service images):
        # find a tracked file with the same name anywhere under static/images/.
        static_index = self._index_static_images()
        for model, field_name in [(HeroSlide, 'image'), (Service, 'image'), (ServiceCategory, 'image')]:
            for obj in model.objects.exclude(**{field_name: ''}):
                src = static_index.get(os.path.basename(getattr(obj, field_name).name))
                if src:
                    self._ensure_file(obj, field_name, src)

        self.stdout.write(self.style.SUCCESS(f'restore_media: {self.restored} file(s) restored'))

    def _index_static_images(self):
        index = {}
        root = os.path.join(settings.BASE_DIR, 'static', 'images')
        for dirpath, _dirs, files in os.walk(root):
            for filename in files:
                index.setdefault(filename, os.path.join(dirpath, filename))
        return index

    def _ensure_file(self, instance, field_name, src_path):
        field = getattr(instance, field_name)
        if not os.path.exists(src_path):
            return

        if field.name:
            # Row already has a path (e.g. from the shared DB): write the file
            # to exactly that path so it lines up without touching the DB.
            target_path = os.path.join(settings.MEDIA_ROOT, field.name)
            if os.path.exists(target_path):
                return
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.copyfile(src_path, target_path)
            self.stdout.write(f'  restored {field.name}')
        else:
            with open(src_path, 'rb') as f:
                field.save(os.path.basename(src_path), ContentFile(f.read()), save=True)
            self.stdout.write(f'  set {field.name}')
        self.restored += 1
