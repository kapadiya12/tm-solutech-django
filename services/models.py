from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field


class ServiceCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='services/categories/', blank=True)
    icon = models.CharField(max_length=50, default='fas fa-cogs')
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)

    # Navbar mega-menu
    show_in_nav = models.BooleanField('Show in navbar', default=True)
    nav_label = models.CharField('Navbar label', max_length=60, blank=True, help_text='Optional shorter name for the navbar. Defaults to the category name.')
    nav_description = models.CharField('Navbar description', max_length=160, blank=True, help_text='One line shown in the navbar. Defaults to the short description.')

    class Meta:
        ordering = ['display_order']
        verbose_name = 'Service Category'
        verbose_name_plural = 'Service Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('services:category_detail', kwargs={'category_slug': self.slug})

    def active_services(self):
        return self.services.filter(is_active=True).order_by('display_order')

    @property
    def menu_label(self):
        return self.name

    @property
    def menu_description(self):
        return self.short_description


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = CKEditor5Field('Description', config_name='extends', blank=True)
    image = models.ImageField(upload_to='services/', blank=True)
    icon = models.CharField(max_length=50, default='fas fa-server')
    features = CKEditor5Field('Features', config_name='extends', blank=True)
    benefits = CKEditor5Field('Benefits', config_name='extends', blank=True)
    process = CKEditor5Field('Process', config_name='extends', blank=True)
    faq = models.TextField(blank=True, help_text='Legacy JSON FAQs (superseded by faq_items).')

    # Structured page sections, edited as rows in the dashboard.
    # The legacy HTML fields above are kept only as a read fallback.
    feature_items = models.JSONField(default=list, blank=True, help_text='[{"icon", "title", "text"}]')
    benefit_items = models.JSONField(default=list, blank=True, help_text='[{"title", "text"}]')
    process_items = models.JSONField(default=list, blank=True, help_text='[{"title", "text"}]')
    faq_items = models.JSONField(default=list, blank=True, help_text='[{"question", "answer"}]')
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    # Navbar mega-menu
    NAV_BADGE_CHOICES = [
        ('', 'None'),
        ('new', 'New'),
        ('popular', 'Popular'),
    ]
    show_in_nav = models.BooleanField('Show in navbar', default=True)
    nav_label = models.CharField('Navbar label', max_length=60, blank=True, help_text='Optional shorter name for the navbar. Defaults to the service title.')
    nav_description = models.CharField('Navbar description', max_length=160, blank=True, help_text='One line shown in the navbar. Defaults to the short description.')
    nav_badge = models.CharField('Navbar badge', max_length=10, choices=NAV_BADGE_CHOICES, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('services:service_detail', kwargs={
            'category_slug': self.category.slug,
            'service_slug': self.slug
        })

    @property
    def menu_label(self):
        return self.title

    @property
    def menu_description(self):
        return self.short_description

    def get_related_services(self):
        return Service.objects.filter(
            category=self.category, is_active=True
        ).exclude(pk=self.pk)[:3]


class Industry(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = CKEditor5Field('Description', config_name='extends', blank=True)
    image = models.ImageField(upload_to='industries/', blank=True)
    icon = models.CharField(max_length=50, default='fas fa-industry')
    benefits = CKEditor5Field('Benefits', config_name='extends', blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)

    class Meta:
        ordering = ['display_order']
        verbose_name_plural = 'Industries'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('services:industry_detail', kwargs={'slug': self.slug})
