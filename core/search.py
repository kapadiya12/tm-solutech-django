"""
Site-wide search shared by the navbar's live (AJAX) search and the /search/ page.

Every word in the query must match (title or description). Results are ranked
so titles that start with the query come first, then titles containing it,
then description-only matches.
"""
import re
from functools import reduce
from operator import and_

from django.db.models import Q
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import Truncator

from cms.models import Page
from insights.models import BlogPost
from services.models import Industry, Service, ServiceCategory

from .models import FAQ

MIN_QUERY_LENGTH = 2

# Fixed site pages, matched on title + keywords
SITE_PAGES = [
    ('About Us', 'core:about', 'fas fa-building', 'company history heritage mission 1985 who we are'),
    ('Leadership', 'core:leadership', 'fas fa-user-tie', 'leaders directors team management ceo'),
    ('Our Clients', 'core:clients', 'fas fa-handshake', 'clients customers trusted organizations industries'),
    ('Why Choose Us', 'core:why_us', 'fas fa-award', 'why us benefits advantages quality'),
    ('All Services', 'services:service_list', 'fas fa-layer-group', 'services solutions offerings'),
    ('Industries', 'services:industry_list', 'fas fa-industry', 'industries sectors verticals'),
    ('Insights', 'insights:post_list', 'fas fa-lightbulb', 'blog insights articles news'),
    ('FAQs', 'core:faqs', 'fas fa-circle-question', 'faq questions answers help'),
    ('Contact', 'contact:contact', 'fas fa-envelope', 'contact consultation phone email address support quote'),
]


def _terms(query):
    return [t for t in re.split(r'\s+', query.strip()) if t][:6]


def _all_terms_q(terms, fields):
    """Every term must appear in at least one of the fields."""
    return reduce(and_, [
        reduce(lambda a, b: a | b, [Q(**{f'{field}__icontains': term}) for field in fields])
        for term in terms
    ])


def _rank(title, query):
    t, q = title.lower(), query.lower()
    if t.startswith(q):
        return 0
    if re.search(r'\b' + re.escape(q), t):
        return 1
    if q in t:
        return 2
    return 3


def _clean(text, words=18):
    return Truncator(strip_tags(text or '').strip()).words(words)


def run_search(query, per_group=5):
    """Return {'query', 'total', 'groups': [{key, label, icon, count, items: [...]}]}."""
    query = (query or '').strip()[:100]
    groups = []
    if len(query) < MIN_QUERY_LENGTH:
        return {'query': query, 'total': 0, 'groups': groups}
    terms = _terms(query)

    def add_group(key, label, icon, items):
        items.sort(key=lambda item: (_rank(item['title'], query), item['title'].lower()))
        if items:
            groups.append({'key': key, 'label': label, 'icon': icon, 'count': len(items), 'items': items[:per_group]})

    services = Service.objects.filter(
        _all_terms_q(terms, ['title', 'nav_label', 'short_description', 'category__name']),
        is_active=True, category__is_active=True,
    ).select_related('category')
    add_group('services', 'Services', 'fas fa-cogs', [{
        'title': s.title,
        'subtitle': _clean(s.menu_description or s.short_description),
        'meta': s.category.name,
        'url': s.get_absolute_url(),
        'icon': s.icon,
        'badge': s.get_nav_badge_display() if s.nav_badge else '',
    } for s in services[:40]])

    categories = ServiceCategory.objects.filter(
        _all_terms_q(terms, ['name', 'nav_label', 'short_description', 'description']), is_active=True,
    )
    add_group('categories', 'Service Areas', 'fas fa-layer-group', [{
        'title': c.name,
        'subtitle': _clean(c.short_description or c.description),
        'meta': 'Service area',
        'url': c.get_absolute_url(),
        'icon': c.icon,
    } for c in categories[:20]])

    industries = Industry.objects.filter(
        _all_terms_q(terms, ['name', 'short_description']), is_active=True,
    )
    add_group('industries', 'Industries', 'fas fa-industry', [{
        'title': i.name,
        'subtitle': _clean(i.short_description),
        'meta': 'Industry',
        'url': i.get_absolute_url(),
        'icon': i.icon,
    } for i in industries[:20]])

    posts = BlogPost.objects.filter(
        _all_terms_q(terms, ['title', 'excerpt']), is_published=True,
    ).select_related('category')
    add_group('insights', 'Insights', 'fas fa-lightbulb', [{
        'title': p.title,
        'subtitle': _clean(p.excerpt),
        'meta': p.published_at.strftime('%d %b %Y') if p.published_at else (p.category.name if p.category else 'Insight'),
        'url': p.get_absolute_url(),
        'icon': 'fas fa-newspaper',
    } for p in posts[:20]])

    lowered = [t.lower() for t in terms]
    pages = []
    for title, url_name, icon, keywords in SITE_PAGES:
        haystack = f'{title} {keywords}'.lower()
        if all(t in haystack for t in lowered):
            pages.append({'title': title, 'subtitle': '', 'meta': 'Page', 'url': reverse(url_name), 'icon': icon})
    for page in Page.objects.filter(_all_terms_q(terms, ['title', 'meta_description']), is_published=True)[:10]:
        pages.append({'title': page.title, 'subtitle': _clean(page.meta_description), 'meta': 'Page', 'url': page.get_absolute_url(), 'icon': 'fas fa-file-lines'})
    add_group('pages', 'Pages', 'fas fa-file-lines', pages)

    faqs = FAQ.objects.filter(_all_terms_q(terms, ['question', 'answer']), is_active=True)
    add_group('faqs', 'FAQs', 'fas fa-circle-question', [{
        'title': f.question,
        'subtitle': _clean(f.answer, 16),
        'meta': f.get_category_display(),
        'url': f"{reverse('core:faqs')}#faq-{f.pk}",
        'icon': 'fas fa-circle-question',
    } for f in faqs[:20]])

    return {'query': query, 'total': sum(g['count'] for g in groups), 'groups': groups}
