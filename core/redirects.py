"""Permanent (301) redirects from the old WordPress site's addresses to the new pages, so search rankings carry over."""
from django.http import HttpResponsePermanentRedirect
from django.urls import path

OLD_TO_NEW = {
    'contacts': '/contact/',
    
    'about_bk': '/about-us/',
    'mission': '/about-us/',
    'our-team': '/leadership/',
    'founder-director': '/leadership/',
    'our-work-model': '/why-us/',
    'our-latest-insight': '/insights/',
    'blog-grid': '/insights/', 'blog-list': '/insights/', 'blog-masonry': '/insights/',
    'portfolio_2-columns': '/work/', 'portfolio-masonry-2': '/work/', 'portfolio-grid-2': '/work/',
    'elements': '/', 'landing': '/', 'typography': '/',
    # service areas moved under /services/
    'cloud-solutions': '/services/cloud-solutions/',
    'network-security': '/services/network-security/',
    'remote-infrastructure-management': '/services/remote-infrastructure-management/',
    # blog posts (old WordPress slugs)
    'custom-copilot-transforming-medical-rep-conversations-with-ai-and-privacy': '/insights/custom-copilot-transforming-medical-rep-conversations/',
    'ensuring-compliance-with-sebis-cybersecurity-framework-tm-solutechs-managed-soc-solution-for-stock-brokers': '/insights/ensuring-compliance-sebi-cybersecurity-framework-managed-soc/',
    'understanding-cscrf-compliance-how-tm-solutech-empowers-sebi-regulated-entities': '/insights/understanding-cscrf-compliance-sebi-regulated-entities/',
}

# /<area>/<old service slug>/  ->  new service slug (same slug unless listed)
SERVICE_RENAMES = {
    'business-continuity-disaster-recovery-bcdr': 'business-continuity-disaster-recovery',
    'next-generation-firewalls-ngfw': 'next-generation-firewalls',
    'quality-of-service-qos': 'quality-of-service',
    'data-privacy-compliance-services': 'data-privacy-compliance',
}
OLD_AREAS = ('cloud-solutions', 'network-security', 'remote-infrastructure-management')


def _to(target):
    return lambda request, **kw: HttpResponsePermanentRedirect(target)


def old_service(request, area, slug):
    return HttpResponsePermanentRedirect(f'/services/{area}/{SERVICE_RENAMES.get(slug, slug)}/')


def old_portfolio(request, slug=None):
    return HttpResponsePermanentRedirect('/work/')


urlpatterns = [path(f'{old}/', _to(new)) for old, new in OLD_TO_NEW.items()]
urlpatterns += [path(f'{area}/<slug:slug>/', old_service, {'area': area}) for area in OLD_AREAS]
urlpatterns += [path('portfolio/', old_portfolio), path('portfolio/<slug:slug>/', old_portfolio)]
