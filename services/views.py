from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404
from .models import ServiceCategory, Service, Industry, ServicePageSettings


def _shared_context():
    """Blocks every service-area page shows: headings, stats, industries, certifications."""
    from core.models import Capability, Certification, ClientLogo, Statistic, Testimonial, WhyUsReason
    return {
        'sp': ServicePageSettings.load(),
        'company_stats': Statistic.objects.filter(is_active=True)[:4],
        'industries': Industry.objects.filter(is_active=True).order_by('display_order'),
        'certifications': Certification.objects.filter(is_active=True),
        'client_logos': ClientLogo.objects.filter(is_active=True),
        'why_us_reasons': WhyUsReason.objects.filter(is_active=True)[:6],
        'capabilities': Capability.objects.filter(is_active=True),
        'testimonials': Testimonial.objects.filter(is_active=True),
    }


def service_list(request):
    # One query for categories + one for all their active services, however
    # many categories exist (the template used to re-query each category 3x).
    active_services = Service.objects.filter(is_active=True).select_related('category').order_by('display_order')
    categories = (
        ServiceCategory.objects.filter(is_active=True)
        .prefetch_related(Prefetch('services', queryset=active_services, to_attr='page_services'))
        .order_by('display_order')
    )
    from core.models import Partner
    context = {
        **_shared_context(),
        'categories': categories,
        'service_total': sum(len(c.page_services) for c in categories),
        'partners': Partner.objects.filter(is_active=True),
        'page_title': 'Our Services',
        'page_subtitle': 'End-to-end IT, from AI and cloud to cybersecurity, networks and hardware: designed, delivered and supported by one certified team.',
    }
    return render(request, 'services/service_list.html', context)


def category_detail(request, category_slug):
    category = get_object_or_404(ServiceCategory, slug=category_slug, is_active=True)
    services = category.active_services().select_related('category')
    context = {
        **_shared_context(),
        'category': category,
        'services': services,
        'partners': category.partners.filter(is_active=True),
        'other_categories': ServiceCategory.objects.filter(is_active=True).exclude(pk=category.pk).prefetch_related(
            Prefetch('services', queryset=Service.objects.filter(is_active=True).order_by('display_order'), to_attr='page_services'),
        ).order_by('display_order'),
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
    related = list(service.get_related_services())
    if len(related) < 4:   # top up with services from other areas so the carousel is never thin
        related += list(Service.objects.filter(is_active=True, category__is_active=True).exclude(
            pk__in=[service.pk] + [r.pk for r in related]).select_related('category').order_by('?')[:6 - len(related)])
    context = {
        **_shared_context(),
        'service': service,
        'partners': service.tech_partners(),
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
