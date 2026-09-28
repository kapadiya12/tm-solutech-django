from .models import ServiceCategory

def service_categories(request):
    categories = ServiceCategory.objects.filter(
        is_active=True
    ).prefetch_related('services').order_by('display_order')
    return {'nav_service_categories': categories}
