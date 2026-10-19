"""Content for the empty state of the navbar search ("what to search for")."""
from collections import Counter

from django import template
from django.core.cache import cache
from django.utils import timezone

register = template.Library()

FALLBACK_TERMS = ['Managed SOC', 'Cloud migration', 'Firewall', 'VAPT', 'AI copilot', 'Office 365']


@register.simple_tag
def search_highlights():
    data = cache.get('search_highlights')
    if data is None:
        from insights.models import BlogPost
        live = BlogPost.objects.filter(is_published=True, published_at__lte=timezone.now()).select_related('category')
        latest = [{'title': p.title, 'url': p.get_absolute_url(), 'meta': p.category.name if p.category else 'Insights',
                   'minutes': p.reading_time} for p in live.order_by('-published_at')[:3]]
        counts = Counter()
        for tags in live.values_list('tags', flat=True):
            counts.update(t.strip() for t in (tags or '').split(',') if t.strip())
        terms = [t for t, _ in counts.most_common(4)]
        for t in FALLBACK_TERMS:
            if len(terms) >= 6:
                break
            if t.lower() not in {x.lower() for x in terms}:
                terms.append(t)
        data = {'latest': latest, 'terms': terms}
        cache.set('search_highlights', data, 300)
    return data
