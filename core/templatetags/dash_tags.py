from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def short_ago(value):
    """'just now', '5 min ago', '3 h ago', 'yesterday', '4 days ago', else 'Mar 12'."""
    if not value:
        return ''
    secs = int((timezone.now() - value).total_seconds())
    if secs < 60:
        return 'just now'
    if secs < 3600:
        return f'{secs // 60} min ago'
    if secs < 86400:
        return f'{secs // 3600} h ago'
    days = secs // 86400
    if days == 1:
        return 'yesterday'
    if days < 7:
        return f'{days} days ago'
    local = timezone.localtime(value)
    return local.strftime('%b %d') if local.year == timezone.localtime().year else local.strftime('%b %d, %Y')
