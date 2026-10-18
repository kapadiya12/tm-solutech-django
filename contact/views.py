import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .forms import MESSAGE_MAX, MESSAGE_MIN, ContactForm, issue_form_token
from .models import ContactPageSettings
from .phone import countries
from core.models import SocialLink
from services.models import ServiceCategory

logger = logging.getLogger(__name__)

RATE_LIMIT_COUNT = 5          # submissions...
RATE_LIMIT_WINDOW = 10 * 60   # ...per 10 minutes per visitor IP


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return (forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR', '')) or 'unknown'


def _rate_limited(request):
    key = f'contact-rate:{_client_ip(request)}'
    count = cache.get(key, 0)
    if count >= RATE_LIMIT_COUNT:
        return True
    cache.set(key, count + 1, RATE_LIMIT_WINDOW)
    return False


def _wants_json(request):
    return request.headers.get('x-requested-with') == 'fetch'


def _company_name():
    try:
        from core.models import SiteSettings
        return SiteSettings.get_settings().company_name or 'TM Solutech'
    except Exception:
        return 'TM Solutech'


def _notify(inquiry, page):
    """Team notification + optional visitor acknowledgement. Failures are logged, never shown."""
    company = _company_name()
    team_body = (
        'New enquiry from the website\n\n'
        f'Service: {inquiry.service or "Not specified"}\n'
        f'Name:    {inquiry.name}\n'
        f'Company: {inquiry.company or "Not provided"}\n'
        f'Email:   {inquiry.email}\n'
        f'Phone:   {inquiry.phone or "Not provided"}\n\n'
        f'Message:\n{inquiry.message}\n'
    )
    try:
        send_mail(
            f'New enquiry from {inquiry.company or inquiry.name}',
            team_body,
            settings.DEFAULT_FROM_EMAIL,
            [page.notify_email or settings.ADMIN_EMAIL],
        )
    except Exception:
        logger.exception('Contact form: team notification email failed (inquiry #%s)', inquiry.pk)

    if not page.send_acknowledgement:
        return
    about = f' about {inquiry.service}' if inquiry.service and inquiry.service != 'Not sure yet' else ''
    ack_body = (
        f'Hi {inquiry.name.split()[0]},\n\n'
        f'Thank you for contacting {company}. We have received your enquiry{about} '
        f'and a member of our team will reply within {page.reply_time}.\n\n'
        'For reference, here is what you sent:\n\n'
        f'{inquiry.message}\n\n'
        f'Regards,\n{company}\n'
    )
    try:
        send_mail(f'We received your enquiry | {company}', ack_body, settings.DEFAULT_FROM_EMAIL, [inquiry.email])
    except Exception:
        logger.exception('Contact form: acknowledgement email failed (inquiry #%s)', inquiry.pk)


def contact_page(request):
    page = ContactPageSettings.get()

    if request.method == 'POST':
        form = ContactForm(request.POST, default_country=page.default_country)
        if _rate_limited(request):
            error = 'Too many messages in a short time. Please wait a few minutes and try again.'
            if _wants_json(request):
                return JsonResponse({'ok': False, 'errors': {'__all__': [error]}}, status=429)
            messages.error(request, error)
            return redirect('contact:contact')

        if form.is_valid():
            if not form.is_spam:
                inquiry = form.save()
                _notify(inquiry, page)
            else:
                logger.info('Contact form: spam submission discarded from %s', _client_ip(request))
            # Bots get the same success response, so they learn nothing
            if _wants_json(request):
                return JsonResponse({'ok': True, 'message': page.success_message, 'form_token': issue_form_token()})
            messages.success(request, page.success_message)
            return redirect('contact:contact')

        if _wants_json(request):
            return JsonResponse({
                'ok': False,
                'errors': {field: [str(e) for e in errs] for field, errs in form.errors.items()},
                'form_token': issue_form_token(),
            }, status=400)
    else:
        initial = {}
        requested = request.GET.get('service', '').strip()
        if requested:
            initial['service'] = requested
        form = ContactForm(initial=initial, default_country=page.default_country)

    context = {
        'form': form,
        'cp': page,
        'form_token': issue_form_token(),
        'phone_countries': countries(),
        'service_icons': {c.name: c.icon for c in ServiceCategory.objects.filter(is_active=True).only('name', 'icon')},
        'contact_socials': [s for s in SocialLink.objects.filter(is_active=True, show_on_contact=True)],
        'message_min': MESSAGE_MIN,
        'message_max': MESSAGE_MAX,
        'page_title': 'Contact Us',
        'page_subtitle': page.page_subtitle,
    }
    return render(request, 'contact/contact.html', context)
