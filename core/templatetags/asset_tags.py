import os

from django import template
from django.conf import settings
from django.templatetags.static import static as static_url

register = template.Library()


@register.simple_tag
def static_v(path):
    """
    Like {% static %}, but appends the source file's mtime as a cache-busting
    query string. This means the browser only re-fetches the file when it has
    actually changed (unlike appending the current timestamp on every
    request, which defeats caching entirely), and unlike no query string at
    all, a change is never masked by the browser's own heuristic caching.
    """
    url = static_url(path)
    if settings.DEBUG:
        for static_dir in settings.STATICFILES_DIRS:
            candidate = os.path.join(static_dir, path)
            if os.path.exists(candidate):
                return f"{url}?v={int(os.path.getmtime(candidate))}"
    return url
