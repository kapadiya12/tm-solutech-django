from .models import SiteSettings, Statistic

def site_settings(request):
    try:
        settings = SiteSettings.get_settings()
    except Exception:
        settings = None
    return {'site_settings': settings}



def nav_stats(request):
    """First two trust-bar statistics, shown in the About mega-menu panel."""
    try:
        return {'nav_stats': Statistic.objects.filter(is_active=True)[:2]}
    except Exception:
        return {'nav_stats': []}
