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
