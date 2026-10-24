from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import RedirectView, TemplateView
from django.templatetags.static import static as static_url


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('services/', include('services.urls')),
    path('insights/', include('insights.urls')),
    path('work/', include('work.urls')),
    path('assistant/', include('assistant.urls')),
    path('contact/', include('contact.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin-dashboard/', include('dashboard.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    # CMS pages last (catch-all for slugs)
    path('', include('cms.urls')),
    # Browser icons: browsers (Safari especially) request these directly and cache them per host
    path('favicon.ico', RedirectView.as_view(url=static_url('images/logo/favicon.png'), permanent=False)),
    path('apple-touch-icon.png', RedirectView.as_view(url=static_url('images/logo/favicon.png'), permanent=False)),
    path('apple-touch-icon-precomposed.png', RedirectView.as_view(url=static_url('images/logo/favicon.png'), permanent=False)),
    # Static pages
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Media (user-uploaded images: leadership photos, client logos, blog images, etc.)
# must be served in production too, not just DEBUG — otherwise every image
# uploaded through the dashboard is a 404 on a host with no separate media
# server/CDN configured. Static files are unaffected: whitenoise already
# serves those in production regardless of this block.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'
handler403 = 'core.views.handler403'
