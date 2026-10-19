from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Count, Q
from django.urls import reverse
from urllib.parse import quote
from .models import (
    SiteSettings, Statistic, WhyUsReason, Testimonial, Leadership, FAQ, FAQCategory, SEOSettings,
    Capability, ClientLogo, HeroTag, HeroStat, HeroSlide,
)
from services.models import ServiceCategory, Service, Industry
from insights.models import BlogPost
from contact.models import ContactInquiry


def home(request):
    context = {
        'statistics': Statistic.objects.filter(is_active=True),
        'service_categories': ServiceCategory.objects.filter(is_active=True).annotate(
            active_service_count=Count('services', filter=Q(services__is_active=True))
        ).order_by('display_order'),  # explicit: Meta.ordering is dropped on GROUP BY queries
        'featured_services': Service.objects.filter(is_featured=True, is_active=True)[:6],
        'why_us_reasons': WhyUsReason.objects.filter(is_active=True)[:6],
        'industries': Industry.objects.filter(is_active=True),
        'testimonials': Testimonial.objects.filter(is_active=True)[:5],
        'leadership': Leadership.objects.filter(is_active=True),
        'latest_posts': BlogPost.objects.filter(is_published=True, published_at__lte=timezone.now()).select_related('category')[:3],
        'capabilities': Capability.objects.filter(is_active=True),
        'client_logos': ClientLogo.objects.filter(is_active=True),
        'hero_tags': HeroTag.objects.filter(is_active=True),
        'hero_stats': HeroStat.objects.filter(is_active=True),
        'hero_slides': HeroSlide.objects.filter(is_active=True),
        'page_title': 'Smart IT Solutions for Modern Businesses',
    }
    return render(request, 'core/home.html', context)


def about(request):
    context = {
        'leadership': Leadership.objects.filter(is_active=True),
        'statistics': Statistic.objects.filter(is_active=True),
        'testimonials': Testimonial.objects.filter(is_active=True),
        'page_title': 'About Us',
        'page_subtitle': 'Learn about TM Solutech and our commitment to delivering exceptional IT solutions',
    }
    return render(request, 'core/about.html', context)


def why_us(request):
    context = {
        'reasons': WhyUsReason.objects.filter(is_active=True),
        'statistics': Statistic.objects.filter(is_active=True),
        'testimonials': Testimonial.objects.filter(is_active=True),
        'page_title': 'Why Choose Us',
        'page_subtitle': 'Discover what makes TM Solutech your ideal technology partner',
    }
    return render(request, 'core/why_us.html', context)


def leadership_page(request):
    context = {
        'leadership': Leadership.objects.filter(is_active=True),
        'page_title': 'Our Leadership',
        'page_subtitle': 'Meet the experienced leaders driving innovation at TM Solutech',
    }
    return render(request, 'core/leadership.html', context)



def clients_page(request):
    context = {
        'client_logos': ClientLogo.objects.filter(is_active=True),
        'statistics': Statistic.objects.filter(is_active=True),
        'industries': Industry.objects.filter(is_active=True),
        'page_title': 'Our Clients',
        'page_subtitle': 'Organizations across industries that trust TM Solutech with their technology',
    }
    return render(request, 'core/clients.html', context)

def faq_page(request):
    from django.db.models import Prefetch
    live = FAQ.objects.filter(is_active=True)
    categories = [c for c in FAQCategory.objects.filter(is_active=True).prefetch_related(
        Prefetch('faqs', queryset=live, to_attr='live_faqs')) if c.live_faqs]
    uncategorised = list(live.filter(category__isnull=True))
    faqs = [f for c in categories for f in c.live_faqs] + uncategorised
    voted = request.session.get('faq_votes', {})
    for f in faqs:
        f.vote = voted.get(str(f.pk))
    context = {
        'categories': categories,
        'uncategorised': uncategorised,
        'faq_count': len(faqs),
        'popular': [f for f in faqs if f.is_popular][:6],
        'faq_schema': faqs,
        'page_title': 'Frequently Asked Questions',
        'page_subtitle': 'Answers about our services, pricing, support and security. Can\'t find yours? Our team is a message away.',
    }
    return render(request, 'core/faq.html', context)


def faq_helpful(request, pk):
    """AJAX: 'Was this helpful?' on an FAQ, one vote per session."""
    from django.db.models import F
    from django.http import JsonResponse
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)
    faq = get_object_or_404(FAQ, pk=pk, is_active=True)
    answer = request.POST.get('answer')
    if answer not in ('yes', 'no'):
        return JsonResponse({'ok': False}, status=400)
    votes = request.session.get('faq_votes', {})
    if str(faq.pk) not in votes:
        field = 'helpful_yes' if answer == 'yes' else 'helpful_no'
        FAQ.objects.filter(pk=faq.pk).update(**{field: F(field) + 1})
        votes[str(faq.pk)] = answer
        request.session['faq_votes'] = votes
    return JsonResponse({'ok': True, 'answer': votes[str(faq.pk)]})


def search(request):
    from .search import run_search
    query = request.GET.get('q', '').strip()
    results = run_search(query, per_group=50)
    context = {
        'query': results['query'],
        'groups': results['groups'],
        'total_results': results['total'],
        'page_title': f'Search results for "{results["query"]}"' if results['query'] else 'Search',
    }
    return render(request, 'core/search.html', context)


def search_suggest(request):
    """JSON for the navbar's live search."""
    from django.http import JsonResponse
    from .search import run_search
    try:
        limit = max(1, min(int(request.GET.get('limit', 4)), 25))
    except ValueError:
        limit = 4
    data = run_search(request.GET.get('q', ''), per_group=limit)
    data['see_all_url'] = f"{reverse('core:search')}?q={quote(data['query'])}" if data['query'] else reverse('core:search')
    response = JsonResponse(data)
    response['Cache-Control'] = 'private, max-age=60'
    return response


def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)

def handler403(request, exception):
    return render(request, 'errors/403.html', status=403)
