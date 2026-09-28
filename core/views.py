from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import SiteSettings, Statistic, WhyUsReason, Testimonial, Leadership, FAQ, SEOSettings
from services.models import ServiceCategory, Service, Industry
from insights.models import BlogPost
from contact.models import ContactInquiry


def home(request):
    context = {
        'statistics': Statistic.objects.filter(is_active=True),
        'service_categories': ServiceCategory.objects.filter(is_active=True).prefetch_related('services'),
        'featured_services': Service.objects.filter(is_featured=True, is_active=True)[:6],
        'why_us_reasons': WhyUsReason.objects.filter(is_active=True)[:6],
        'industries': Industry.objects.filter(is_active=True)[:6],
        'testimonials': Testimonial.objects.filter(is_active=True)[:5],
        'leadership': Leadership.objects.filter(is_active=True)[:5],
        'latest_posts': BlogPost.objects.filter(is_published=True)[:3],
        'page_title': 'Smart IT Solutions for Modern Businesses',
    }
    return render(request, 'core/home.html', context)


def about(request):
    context = {
        'leadership': Leadership.objects.filter(is_active=True),
        'statistics': Statistic.objects.filter(is_active=True),
        'testimonials': Testimonial.objects.filter(is_active=True),
        'page_title': 'About Us',
        'page_subtitle': 'Learn about TM Solutech and our commitment to delivering exceptional IT solutions',
    }
    return render(request, 'core/about.html', context)


def why_us(request):
    context = {
        'reasons': WhyUsReason.objects.filter(is_active=True),
        'statistics': Statistic.objects.filter(is_active=True),
        'testimonials': Testimonial.objects.filter(is_active=True),
        'page_title': 'Why Choose Us',
        'page_subtitle': 'Discover what makes TM Solutech your ideal technology partner',
    }
    return render(request, 'core/why_us.html', context)


def leadership_page(request):
    context = {
        'leadership': Leadership.objects.filter(is_active=True),
        'page_title': 'Our Leadership',
        'page_subtitle': 'Meet the experienced leaders driving innovation at TM Solutech',
    }
    return render(request, 'core/leadership.html', context)


def faq_page(request):
    faqs = FAQ.objects.filter(is_active=True)
    categories = faqs.values_list('category', flat=True).distinct()
    context = {
        'faqs': faqs,
        'categories': categories,
        'page_title': 'Frequently Asked Questions',
        'page_subtitle': 'Find answers to common questions about our services',
    }
    return render(request, 'core/faq.html', context)


def search(request):
    query = request.GET.get('q', '').strip()
    results = {
        'services': [],
        'posts': [],
        'industries': [],
    }
    if query:
        results['services'] = Service.objects.filter(
            Q(title__icontains=query) | Q(short_description__icontains=query),
            is_active=True
        )[:10]
        results['posts'] = BlogPost.objects.filter(
            Q(title__icontains=query) | Q(excerpt__icontains=query),
            is_published=True
        )[:10]
        results['industries'] = Industry.objects.filter(
            Q(name__icontains=query) | Q(short_description__icontains=query),
            is_active=True
        )[:10]
    total = sum(len(v) for v in results.values())
    context = {
        'query': query,
        'results': results,
        'total_results': total,
        'page_title': f'Search Results for "{query}"' if query else 'Search',
    }
    return render(request, 'core/search.html', context)


def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)

def handler403(request, exception):
    return render(request, 'errors/403.html', status=403)
