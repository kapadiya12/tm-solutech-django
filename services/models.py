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
    faq = models.TextField(blank=True, help_text='JSON format: [{"question": "...", "answer": "..."}]')
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
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
