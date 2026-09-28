from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field


class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = CKEditor5Field('Content', config_name='extends', blank=True)
    featured_image = models.ImageField(upload_to='pages/', blank=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    show_in_footer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('cms:page_detail', kwargs={'slug': self.slug})
