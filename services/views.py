from django.shortcuts import render, get_object_or_404
from .models import ServiceCategory, Service, Industry


def service_list(request):
    categories = ServiceCategory.objects.filter(
        is_active=True
    ).prefetch_related('services')
    context = {
        'categories': categories,
        'page_title': 'Our Services',
        'page_subtitle': 'Comprehensive IT solutions tailored to your business needs',
    }
    return render(request, 'services/service_list.html', context)


def category_detail(request, category_slug):
    category = get_object_or_404(ServiceCategory, slug=category_slug, is_active=True)
    services = category.active_services()
    context = {
        'category': category,
        'services': services,
        'page_title': category.name,
        'page_subtitle': category.short_description or category.description[:200] if category.description else '',
    }
    return render(request, 'services/category_detail.html', context)


def service_detail(request, category_slug, service_slug):
    service = get_object_or_404(
        Service.objects.select_related('category'),
        slug=service_slug,
        category__slug=category_slug,
        is_active=True
    )
    faqs = service.faq_items
    if not faqs and service.faq:
        import json
        try:
            faqs = json.loads(service.faq)
        except (json.JSONDecodeError, TypeError):
            faqs = []
    related = service.get_related_services()
    context = {
        'service': service,
        'category': service.category,
        'faqs': faqs,
        'related_services': related,
        'page_title': service.title,
        'page_subtitle': service.short_description,
    }
    return render(request, 'services/service_detail.html', context)


def industry_list(request):
    industries = Industry.objects.filter(is_active=True)
    context = {
        'industries': industries,
        'page_title': 'Industries We Serve',
        'page_subtitle': 'Delivering specialized IT solutions across diverse industry verticals',
    }
    return render(request, 'services/industry_list.html', context)


def industry_detail(request, slug):
    industry = get_object_or_404(Industry, slug=slug, is_active=True)
    context = {
        'industry': industry,
        'page_title': industry.name,
        'page_subtitle': industry.short_description,
    }
    return render(request, 'services/industry_detail.html', context)
