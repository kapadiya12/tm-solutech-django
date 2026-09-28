from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


class SiteSettings(models.Model):
    company_name = models.CharField(max_length=200, default='TM Solutech Private Limited')
    tagline = models.CharField(max_length=300, blank=True)
    logo = models.ImageField(upload_to='settings/', blank=True)
    favicon = models.ImageField(upload_to='settings/', blank=True)
    phone = models.CharField(max_length=20, default='+91 7947717070')
    email = models.EmailField(default='info@tmsolutech.com')
    address = models.TextField(default='805/806 Aditya Building, Near Mithakhali Six Roads, Ellisbridge, Ahmedabad, Gujarat 380006')
    google_maps_url = models.URLField(blank=True)
    google_maps_embed = models.TextField(blank=True, help_text='Google Maps embed iframe code')
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    footer_description = models.TextField(blank=True)
    copyright_text = models.CharField(max_length=300, blank=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)
    og_image = models.ImageField(upload_to='settings/', blank=True)
    header_scripts = models.TextField(blank=True, help_text='Scripts to add in <head>')
    footer_scripts = models.TextField(blank=True, help_text='Scripts to add before </body>')

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        # Ensure only one instance
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Statistic(models.Model):
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=50)
    suffix = models.CharField(max_length=20, blank=True, help_text='e.g., +, %, K')
    icon = models.CharField(max_length=50, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return f"{self.label}: {self.value}{self.suffix}"


class WhyUsReason(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='fas fa-check-circle')
    image = models.ImageField(upload_to='why_us/', blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order']
        verbose_name = 'Why Us Reason'
        verbose_name_plural = 'Why Us Reasons'

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    name = models.CharField(max_length=200)
    designation = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    photo = models.ImageField(upload_to='testimonials/', blank=True)
    rating = models.PositiveIntegerField(default=5, choices=[(i, str(i)) for i in range(1, 6)])
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return f"{self.name} - {self.company}"


class Gallery(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gallery/')
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order']
        verbose_name_plural = 'Galleries'

    def __str__(self):
        return self.title


class SEOSettings(models.Model):
    page_name = models.CharField(max_length=100, unique=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)
    og_title = models.CharField(max_length=200, blank=True)
    og_description = models.TextField(blank=True)
    og_image = models.ImageField(upload_to='seo/', blank=True)
    structured_data = models.TextField(blank=True, help_text='JSON-LD structured data')

    class Meta:
        verbose_name = 'SEO Settings'
        verbose_name_plural = 'SEO Settings'

    def __str__(self):
        return f"SEO - {self.page_name}"


class Leadership(models.Model):
    name = models.CharField(max_length=200)
    designation = models.CharField(max_length=200)
    short_bio = models.TextField(blank=True)
    biography = CKEditor5Field('Biography', config_name='extends', blank=True)
    photo = models.ImageField(upload_to='leadership/')
    linkedin_url = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order']
        verbose_name_plural = 'Leadership'

    def __str__(self):
        return f"{self.name} - {self.designation}"


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('services', 'Services'),
        ('cloud', 'Cloud Solutions'),
        ('network', 'Network & Security'),
        ('infrastructure', 'Infrastructure'),
        ('billing', 'Billing'),
        ('support', 'Support'),
    ]

    question = models.CharField(max_length=500)
    answer = CKEditor5Field('Answer', config_name='default')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question
