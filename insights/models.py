from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field
import math


class BlogCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'

    def __str__(self):
        return self.name

    def post_count(self):
        return self.posts.filter(is_published=True, published_at__lte=timezone.now()).count()


class BlogPost(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    featured_image = models.ImageField(upload_to='blog/', blank=True)
    excerpt = models.TextField(max_length=500, blank=True)
    content = CKEditor5Field('Content', config_name='extends')
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('insights:post_detail', kwargs={'slug': self.slug})

    @property
    def reading_time(self):
        if self.content:
            word_count = len(self.content.split())
            return max(1, math.ceil(word_count / 200))
        return 1

    def get_related_posts(self):
        if self.category:
            return BlogPost.objects.filter(
                category=self.category, is_published=True,
                published_at__lte=timezone.now()
            ).exclude(pk=self.pk)[:3]
        return BlogPost.objects.filter(
            is_published=True, published_at__lte=timezone.now()
        ).exclude(pk=self.pk)[:3]
