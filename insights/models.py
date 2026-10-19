from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
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
    tags = models.CharField(max_length=250, blank=True, help_text='Comma separated, e.g. Cloud, Security, Compliance')

    # Engagement (updated by the site, not edited by hand)
    view_count = models.PositiveIntegerField(default=0, editable=False)
    helpful_yes = models.PositiveIntegerField(default=0, editable=False)
    helpful_no = models.PositiveIntegerField(default=0, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('insights:post_detail', kwargs={'slug': self.slug})

    @property
    def word_count(self):
        return len(strip_tags(self.content or '').split())

    @property
    def reading_time(self):
        return max(1, math.ceil(self.word_count / 200))

    @property
    def tag_list(self):
        return [t.strip() for t in (self.tags or '').split(',') if t.strip()]

    @property
    def status(self):
        if not self.is_published:
            return 'draft'
        if self.published_at and self.published_at > timezone.now():
            return 'scheduled'
        return 'published'

    @property
    def status_label(self):
        return {'draft': 'Draft', 'scheduled': 'Scheduled', 'published': 'Published'}[self.status]

    @property
    def helpful_total(self):
        return self.helpful_yes + self.helpful_no

    @property
    def helpful_percent(self):
        return round(100 * self.helpful_yes / self.helpful_total) if self.helpful_total else None

    def get_related_posts(self, limit=3):
        live = BlogPost.objects.filter(is_published=True, published_at__lte=timezone.now()).exclude(pk=self.pk).select_related('category')
        same = list(live.filter(category=self.category)[:limit]) if self.category else []
        if len(same) < limit:
            same += list(live.exclude(pk__in=[p.pk for p in same]).order_by('-view_count', '-published_at')[:limit - len(same)])
        return same


class BlogPostDailyView(models.Model):
    """Views per post per day (powers the admin charts)."""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='daily_views')
    date = models.DateField()
    views = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('post', 'date')
        ordering = ['-date']

    def __str__(self):
        return f'{self.post_id} {self.date}: {self.views}'
