from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone


class StaticSitemap(Sitemap):
    changefreq = 'weekly'

    def items(self):
        return ['core:home', 'core:about', 'core:why_us', 'core:leadership', 'core:clients', 'core:faqs',
                'services:service_list', 'services:industry_list', 'insights:post_list', 'work:list', 'contact:contact']

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return 1.0 if item == 'core:home' else 0.8


class ServiceCategorySitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        from services.models import ServiceCategory
        return ServiceCategory.objects.filter(is_active=True).order_by('display_order')


class ServiceSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        from services.models import Service
        return Service.objects.filter(is_active=True, category__is_active=True).select_related('category').order_by('pk')

    def lastmod(self, obj):
        return obj.updated_at


class IndustrySitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        from services.models import Industry
        return Industry.objects.filter(is_active=True).order_by('display_order')


class PostSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        from insights.models import BlogPost
        return BlogPost.objects.filter(is_published=True, published_at__lte=timezone.now()).order_by('-published_at')

    def lastmod(self, obj):
        return obj.updated_at


class CaseStudySitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        from work.models import CaseStudy
        return CaseStudy.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class PageSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        from cms.models import Page
        return Page.objects.filter(is_published=True)


SITEMAPS = {
    'static': StaticSitemap, 'service-areas': ServiceCategorySitemap, 'services': ServiceSitemap,
    'industries': IndustrySitemap, 'insights': PostSitemap, 'work': CaseStudySitemap, 'pages': PageSitemap,
}
