from django.db.models import Count, Prefetch, Q

from .models import Service, ServiceCategory


def service_categories(request):
    """Services mega-menu data: navbar-visible categories with their navbar-visible services."""
    nav_services = Service.objects.filter(is_active=True, show_in_nav=True).order_by('display_order')
    categories = (
        ServiceCategory.objects.filter(is_active=True, show_in_nav=True)
        .annotate(nav_service_count=Count('services', filter=Q(services__is_active=True, services__show_in_nav=True)))
        .prefetch_related(Prefetch('services', queryset=nav_services, to_attr='nav_services'))
        .order_by('display_order')
    )
    return {
        'nav_service_categories': categories,
        'nav_service_total': sum(category.nav_service_count for category in categories),
    }
