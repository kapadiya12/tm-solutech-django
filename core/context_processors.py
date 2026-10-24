from .models import SiteSettings, Statistic

def site_settings(request):
    try:
        settings = SiteSettings.get_settings()
    except Exception:
        settings = None
    return {'site_settings': settings}



def nav_stats(request):
    """First two trust-bar statistics, shown in the Why Us mega-menu panel."""
    try:
        return {'nav_stats': Statistic.objects.filter(is_active=True)[:2]}
    except Exception:
        return {'nav_stats': []}


def social_links(request):
    """Active social profiles (footer + contact page)."""
    try:
        from .models import SocialLink
        return {'social_links': list(SocialLink.objects.filter(is_active=True))}
    except Exception:
        return {'social_links': []}


BANNER_KEYS = {
    'contact': 'contact', 'why_us': 'why-us', 'about': 'about', 'leadership': 'leadership', 'clients': 'clients',
    'industry_list': 'industries', 'industry_detail': 'industries', 'faqs': 'faqs', 'post_list': 'insights',
    'search': 'default',
}


def page_banner(request):
    """The banner photo for the current page (Admin → Page Banners)."""
    match = getattr(request, 'resolver_match', None)
    if not match or request.path.startswith(('/admin-dashboard/', '/admin/', '/accounts/')):
        return {}
    key = BANNER_KEYS.get(match.url_name)
    if match.app_name == 'work' and match.url_name == 'list':
        key = 'work'
    elif match.app_name == 'cms':
        key = match.kwargs.get('slug') or 'default'
    if not key:
        return {}
    from .models import PageBanner
    banners = {b.page: b for b in PageBanner.objects.filter(is_active=True, page__in=[key, 'default'])}
    return {'page_banner': banners.get(key) or banners.get('default')}
