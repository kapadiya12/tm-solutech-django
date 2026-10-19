import re

from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import BlogCategory, BlogPost, BlogPostDailyView

PER_PAGE = 9
SORTS = {
    'latest': ('-published_at', 'Latest'),
    'popular': ('-view_count', 'Most read'),
    'oldest': ('published_at', 'Oldest'),
}
BOT_RE = re.compile(r'bot|crawl|spider|slurp|preview|facebookexternalhit|curl|wget|python-requests|headless', re.I)


def _live_posts():
    return BlogPost.objects.filter(is_published=True, published_at__lte=timezone.now())


def _filtered(request):
    posts = _live_posts().select_related('category', 'author')
    category = request.GET.get('category', '').strip()
    q = request.GET.get('q', '').strip()[:100]
    tag = request.GET.get('tag', '').strip()[:50]
    sort = request.GET.get('sort', 'latest')
    if sort not in SORTS:
        sort = 'latest'
    if category:
        posts = posts.filter(category__slug=category)
    if tag:
        posts = posts.filter(tags__icontains=tag)
    if q:
        for word in q.split()[:6]:
            posts = posts.filter(
                Q(title__icontains=word) | Q(excerpt__icontains=word) | Q(content__icontains=word)
                | Q(tags__icontains=word) | Q(category__name__icontains=word)
            )
    return posts.order_by(SORTS[sort][0], '-pk'), {'category': category, 'q': q, 'tag': tag, 'sort': sort}


def _categories():
    now = timezone.now()
    return BlogCategory.objects.filter(is_active=True).annotate(
        live_count=Count('posts', filter=Q(posts__is_published=True, posts__published_at__lte=now))
    ).filter(live_count__gt=0)


def _featured_split(posts, f):
    """On the unfiltered 'Latest' view the featured post sits in its own slot, never twice."""
    if f['category'] or f['q'] or f['tag'] or f['sort'] != 'latest':
        return None, posts
    featured = posts.filter(is_featured=True).first() or posts.first()
    return featured, (posts.exclude(pk=featured.pk) if featured else posts)


def post_list(request):
    posts, f = _filtered(request)
    filtering = bool(f['category'] or f['q'] or f['tag'])
    featured, posts = _featured_split(posts, f)
    page = Paginator(posts, PER_PAGE).get_page(request.GET.get('page'))
    categories = list(_categories())
    context = {
        'active_category': next((c for c in categories if c.slug == f['category']), None),
        'posts': page,
        'featured_post': featured,
        'categories': categories,
        'all_count': _live_posts().count(),
        'sorts': [(k, v[1]) for k, v in SORTS.items()],
        'filters': f,
        'filtering': filtering,
        'result_count': page.paginator.count,
        'popular': _live_posts().select_related('category').order_by('-view_count', '-published_at')[:4],
        'page_title': 'Insights',
        'page_subtitle': 'Ideas, guides and news on cloud, cybersecurity, AI and IT infrastructure.',
    }
    return render(request, 'insights/post_list.html', context)


def post_search(request):
    """AJAX: filtered cards (live search, category chips, sort, load more) + quick suggestions."""
    posts, f = _filtered(request)
    suggest_from = posts
    featured, posts = _featured_split(posts, f)
    page = Paginator(posts, PER_PAGE).get_page(request.GET.get('page'))
    html = render_to_string('insights/_cards.html', {'posts': page}, request=request)
    suggestions = []
    if f['q']:
        for p in suggest_from[:5]:
            suggestions.append({
                'title': p.title, 'url': p.get_absolute_url(),
                'category': p.category.name if p.category else '',
                'minutes': p.reading_time,
            })
    return JsonResponse({
        'html': html,
        'count': page.paginator.count + (1 if featured else 0),
        'featured': bool(featured),
        'page': page.number,
        'has_next': page.has_next(),
        'suggestions': suggestions,
    })


def _record_view(request, post):
    """One view per visitor session per post; bots ignored."""
    if BOT_RE.search(request.META.get('HTTP_USER_AGENT', '')):
        return
    seen = request.session.get('seen_posts', [])
    if post.pk in seen:
        return
    seen.append(post.pk)
    request.session['seen_posts'] = seen[-200:]
    BlogPost.objects.filter(pk=post.pk).update(view_count=F('view_count') + 1)
    today = timezone.localdate()
    row, created = BlogPostDailyView.objects.get_or_create(post=post, date=today, defaults={'views': 1})
    if not created:
        BlogPostDailyView.objects.filter(pk=row.pk).update(views=F('views') + 1)
    post.view_count += 1


def post_detail(request, slug):
    post = get_object_or_404(_live_posts().select_related('category', 'author'), slug=slug)
    _record_view(request, post)
    live = _live_posts()
    newer = live.filter(published_at__gt=post.published_at).order_by('published_at').first()
    older = live.filter(published_at__lt=post.published_at).order_by('-published_at').first()
    voted = request.session.get('helpful_votes', {}).get(str(post.pk))
    return render(request, 'insights/post_detail.html', {
        'post': post,
        'related_posts': post.get_related_posts(),
        'newer': newer,
        'older': older,
        'voted': voted,
        'page_title': post.title,
    })


@require_POST
def post_helpful(request, slug):
    """AJAX: 'Was this helpful?' vote, one per session per post."""
    post = get_object_or_404(_live_posts(), slug=slug)
    answer = request.POST.get('answer')
    if answer not in ('yes', 'no'):
        return JsonResponse({'ok': False}, status=400)
    votes = request.session.get('helpful_votes', {})
    if str(post.pk) not in votes:
        field = 'helpful_yes' if answer == 'yes' else 'helpful_no'
        BlogPost.objects.filter(pk=post.pk).update(**{field: F(field) + 1})
        votes[str(post.pk)] = answer
        request.session['helpful_votes'] = votes
    return JsonResponse({'ok': True, 'answer': votes[str(post.pk)]})
