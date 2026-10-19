from django.db import models
from django.urls import reverse

from services.models import Industry, Service


class CaseStudy(models.Model):
    """A past project shown on the Our Work page."""
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    client_name = models.CharField(max_length=120, blank=True)
    client_logo = models.ImageField(upload_to='work/logos/', blank=True)
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True, blank=True, related_name='case_studies')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='case_studies')
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    summary = models.CharField(max_length=300)
    cover_image = models.ImageField(upload_to='work/', blank=True)
    challenge = models.TextField()
    solution = models.TextField()
    results = models.TextField(blank=True)
    metrics = models.TextField(blank=True)
    testimonial_quote = models.TextField(blank=True)
    testimonial_author = models.CharField(max_length=160, blank=True)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Case study'
        verbose_name_plural = 'Case studies'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('work:detail', kwargs={'slug': self.slug})

    @property
    def client_display(self):
        return self.client_name or 'Confidential client'

    @property
    def metric_list(self):
        """'40% | Less downtime' per line -> [{'value': '40%', 'label': 'Less downtime'}]."""
        out = []
        for line in self.metrics.splitlines():
            if '|' in line:
                value, label = (p.strip() for p in line.split('|', 1))
                if value and label:
                    out.append({'value': value, 'label': label})
        return out[:4]

    @property
    def result_list(self):
        return [line.strip(' -•\t') for line in self.results.splitlines() if line.strip(' -•\t')]

    @property
    def is_complete(self):
        return bool(self.summary and self.challenge and self.solution and (self.results or self.metrics))
