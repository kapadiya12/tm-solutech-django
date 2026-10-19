from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Count, F, Max, Prefetch, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from django.core.management import call_command
import io
import json

from core.models import (
    SiteSettings, Statistic, WhyUsReason, Testimonial, Leadership, FAQ, SEOSettings, Gallery,
    Capability, ClientLogo, HeroTag, HeroStat, HeroSlide,
)
from services.models import ServiceCategory, Service, Industry
from insights.models import BlogPost, BlogCategory
from contact.models import ContactInquiry
from cms.models import Page


def staff_required(view_func):
    return user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='accounts:login'
    )(view_func)


def superuser_required(view_func):
    return user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url='accounts:login'
    )(view_func)


@login_required
@superuser_required
def run_migrations(request):
    """
    One-click 'migrate' / 'sync_seed_media' for hosts (like Render's free
    tier) with no shell access. Runs in-process, in the exact same
    environment/filesystem that serves the live site, so it's more reliable
    here than trying to get a platform's Build Command configured correctly.

    These are two separate actions because they solve different problems:
    'migrate' applies schema changes (and is a no-op if already applied —
    migration state lives in the shared database, not on this filesystem).
    'sync_seed_media' copies seed images onto disk wherever they're missing,
    regardless of migration state — needed because the database can already
    say an image is set while the actual file was never written on *this*
    environment's disk (e.g. it was only ever run locally before).
    """
    output = None
    error = None
    action = None
    if request.method == 'POST':
        action = request.POST.get('action', 'migrate')
        command = 'migrate' if action == 'migrate' else 'sync_seed_media'
        buffer = io.StringIO()
        try:
            if command == 'migrate':
                call_command(command, interactive=False, stdout=buffer, stderr=buffer)
            else:
                call_command(command, stdout=buffer, stderr=buffer)
            output = buffer.getvalue()
            messages.success(request, f'{command} ran successfully.')
        except Exception as e:
            error = f"{buffer.getvalue()}\n{e}"
            messages.error(request, f'{command} failed — see details below.')
    return render(request, 'dashboard/run_migrations.html', {
        'page_title': 'Run Migrations',
        'output': output,
        'error': error,
    })


@login_required
@staff_required
def dashboard_index(request):
    now = timezone.now()
    last_30 = now - timedelta(days=30)
    prev_30 = now - timedelta(days=60)

    inquiries = ContactInquiry.objects.all()
    recent_count = inquiries.filter(created_at__gte=last_30).count()
    previous_count = inquiries.filter(created_at__gte=prev_30, created_at__lt=last_30).count()
    if previous_count:
        trend = round((recent_count - previous_count) / previous_count * 100)
    else:
        trend = None  # no baseline to compare against

    # Last 12 calendar months, zero-filled so the chart always has a full axis
    months = []
    y, m = now.year, now.month
    for _ in range(12):
        months.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    months.reverse()
    from datetime import datetime as _dt
    start = timezone.make_aware(_dt(months[0][0], months[0][1], 1))
    counts = {
        (d['month'].year, d['month'].month): d['count']
        for d in inquiries.filter(created_at__gte=start).annotate(month=TruncMonth('created_at')).values('month').annotate(count=Count('id'))
    }
    import calendar
    chart_labels = [f"{calendar.month_abbr[mm]} {str(yy)[2:]}" for yy, mm in months]
    chart_data = [counts.get(k, 0) for k in months]

    status_counts = {row['status']: row['count'] for row in inquiries.values('status').annotate(count=Count('id'))}
    status_rows = [
        {'key': key, 'label': label, 'count': status_counts.get(key, 0)}
        for key, label in ContactInquiry.STATUS_CHOICES
    ]

    services = Service.objects.all()
    categories = ServiceCategory.objects.all()
    health = [
        {'label': 'Service categories', 'value': categories.filter(is_active=True).count(), 'icon': 'fas fa-layer-group', 'url': 'dashboard:category_list', 'note': f"{categories.filter(is_active=False).count()} hidden"},
        {'label': 'Services published', 'value': services.filter(is_active=True).count(), 'icon': 'fas fa-cogs', 'url': 'dashboard:service_list', 'note': f"{services.filter(show_in_nav=False).count()} not in navbar"},
        {'label': 'Hero slides', 'value': HeroSlide.objects.filter(is_active=True).count(), 'icon': 'fas fa-images', 'url': 'dashboard:heroslide_list', 'note': 'on the homepage'},
        {'label': 'Industries', 'value': Industry.objects.filter(is_active=True).count(), 'icon': 'fas fa-industry', 'url': 'dashboard:industry_list', 'note': 'active'},
        {'label': 'Leadership', 'value': Leadership.objects.filter(is_active=True).count(), 'icon': 'fas fa-user-tie', 'url': 'dashboard:leadership_list', 'note': 'profiles'},
        {'label': 'Client logos', 'value': ClientLogo.objects.filter(is_active=True).count(), 'icon': 'fas fa-building', 'url': 'dashboard:clientlogo_list', 'note': 'in the logo strip'},
        {'label': 'FAQs', 'value': FAQ.objects.filter(is_active=True).count(), 'icon': 'fas fa-circle-question', 'url': 'dashboard:faq_list', 'note': 'answered'},
        {'label': 'Pages', 'value': Page.objects.filter(is_published=True).count(), 'icon': 'fas fa-file-lines', 'url': 'dashboard:page_list', 'note': 'published'},
    ]

    hour = timezone.localtime(now).hour
    greeting = 'Good morning' if hour < 12 else 'Good afternoon' if hour < 17 else 'Good evening'

    context = {
        'greeting': greeting,
        'today': timezone.localtime(now),
        'total_services': services.filter(is_active=True).count(),
        'total_categories': categories.filter(is_active=True).count(),
        'published_posts': BlogPost.objects.filter(is_published=True).count(),
        'draft_posts': BlogPost.objects.filter(is_published=False).count(),
        'total_inquiries': inquiries.count(),
        'recent_inquiry_count': recent_count,
        'inquiry_trend': trend,
        'new_inquiries': inquiries.filter(status='new').count(),
        'recent_inquiries': inquiries.order_by('-created_at')[:6],
        'recent_posts': BlogPost.objects.select_related('category').order_by('-created_at')[:5],
        'status_rows': status_rows,
        'health': health,
        'chart': {'labels': chart_labels, 'data': chart_data, 'status': [r['count'] for r in status_rows], 'status_labels': [r['label'] for r in status_rows]},
        'page_title': 'Dashboard',
    }
    return render(request, 'dashboard/index.html', context)


# ---- Services CRUD ----
def _after_save(request, obj, list_url, edit_url):
    """'Save & keep editing' stays on the form; plain Save returns to the list."""
    if 'save_continue' in request.POST:
        return redirect(edit_url, pk=obj.pk)
    return redirect(list_url)


@login_required
@staff_required
def service_list(request):
    services = Service.objects.select_related('category').order_by('category__display_order', 'display_order')
    categories = ServiceCategory.objects.annotate(service_count=Count('services')).order_by('display_order')
    q = request.GET.get('q', '').strip()
    cat = request.GET.get('category', '')
    status = request.GET.get('status', '')
    if q:
        services = services.filter(Q(title__icontains=q) | Q(short_description__icontains=q))
    if cat.isdigit():
        services = services.filter(category_id=int(cat))
    if status == 'published':
        services = services.filter(is_active=True)
    elif status == 'hidden':
        services = services.filter(is_active=False)
    elif status == 'not_in_nav':
        services = services.filter(show_in_nav=False)
    context = {
        'services': services,
        'categories': categories,
        'total': Service.objects.count(),
        'q': q, 'current_category': cat, 'current_status': status,
        'page_title': 'Services',
    }
    return render(request, 'dashboard/services/list.html', context)


def _service_form_context(form, title, service=None):
    return {
        'form': form,
        'service': service,
        'page_title': title,
        'category_slugs': {str(c.pk): c.slug for c in ServiceCategory.objects.all()},
    }


@login_required
@staff_required
def service_create(request):
    from dashboard.forms import ServiceForm
    initial = {}
    if request.GET.get('category', '').isdigit():
        initial['category'] = int(request.GET['category'])
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            last = Service.objects.filter(category=service.category).order_by('-display_order').values_list('display_order', flat=True).first()
            service.display_order = (last or 0) + 1
            service.save()
            messages.success(request, f'"{service.title}" created. Its page is live at {service.get_absolute_url()}')
            return _after_save(request, service, 'dashboard:service_list', 'dashboard:service_edit')
        messages.error(request, 'Please fix the highlighted fields.')
    else:
        form = ServiceForm(initial=initial)
    return render(request, 'dashboard/services/form.html', _service_form_context(form, 'Add Service'))


@login_required
@staff_required
def service_edit(request, pk):
    from dashboard.forms import ServiceForm
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        old_category = service.category_id
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            service = form.save(commit=False)
            if service.category_id != old_category:
                last = Service.objects.filter(category_id=service.category_id).exclude(pk=service.pk).order_by('-display_order').values_list('display_order', flat=True).first()
                service.display_order = (last or 0) + 1
            service.save()
            messages.success(request, f'"{service.title}" saved.')
            return _after_save(request, service, 'dashboard:service_list', 'dashboard:service_edit')
        messages.error(request, 'Please fix the highlighted fields.')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'dashboard/services/form.html', _service_form_context(form, 'Edit Service', service))


@login_required
@staff_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        name = service.title
        service.delete()
        messages.success(request, f'"{name}" deleted.')
    return redirect('dashboard:service_list')


# ---- Category CRUD ----
@login_required
@staff_required
def category_list(request):
    categories = ServiceCategory.objects.annotate(
        service_count=Count('services'),
        live_count=Count('services', filter=Q(services__is_active=True)),
    ).order_by('display_order')
    return render(request, 'dashboard/categories/list.html', {'categories': categories, 'page_title': 'Service Categories'})


@login_required
@staff_required
def category_create(request):
    from dashboard.forms import ServiceCategoryForm
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            last = ServiceCategory.objects.order_by('-display_order').values_list('display_order', flat=True).first()
            category.display_order = (last or 0) + 1
            category.save()
            messages.success(request, f'Category "{category.name}" created. Now add services to it.')
            return _after_save(request, category, 'dashboard:category_list', 'dashboard:category_edit')
        messages.error(request, 'Please fix the highlighted fields.')
    else:
        form = ServiceCategoryForm()
    return render(request, 'dashboard/categories/form.html', {'form': form, 'page_title': 'Add Category'})


@login_required
@staff_required
def category_edit(request, pk):
    from dashboard.forms import ServiceCategoryForm
    category = get_object_or_404(ServiceCategory, pk=pk)
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" saved.')
            return _after_save(request, category, 'dashboard:category_list', 'dashboard:category_edit')
        messages.error(request, 'Please fix the highlighted fields.')
    else:
        form = ServiceCategoryForm(instance=category)
    services = category.services.order_by('display_order')
    return render(request, 'dashboard/categories/form.html', {'form': form, 'category': category, 'services': services, 'page_title': 'Edit Category'})


@login_required
@staff_required
def category_delete(request, pk):
    category = get_object_or_404(ServiceCategory, pk=pk)
    if request.method == 'POST':
        count = category.services.count()
        if count:
            messages.error(request, f'"{category.name}" still has {count} service{"s" if count != 1 else ""}. Move or delete them first, so no service is lost by accident.')
        else:
            category.delete()
            messages.success(request, f'Category "{category.name}" deleted.')
    return redirect('dashboard:category_list')


# ---- Industry CRUD ----
@login_required
@staff_required
def industry_list(request):
    industries = Industry.objects.all()
    return render(request, 'dashboard/industries/list.html', {'industries': industries, 'page_title': 'Manage Industries'})


@login_required
@staff_required
def industry_create(request):
    from dashboard.forms import IndustryForm
    if request.method == 'POST':
        form = IndustryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Industry created.')
            return redirect('dashboard:industry_list')
    else:
        form = IndustryForm()
    return render(request, 'dashboard/industries/form.html', {'form': form, 'page_title': 'Add Industry'})


@login_required
@staff_required
def industry_edit(request, pk):
    from dashboard.forms import IndustryForm
    industry = get_object_or_404(Industry, pk=pk)
    if request.method == 'POST':
        form = IndustryForm(request.POST, request.FILES, instance=industry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Industry updated.')
            return redirect('dashboard:industry_list')
    else:
        form = IndustryForm(instance=industry)
    return render(request, 'dashboard/industries/form.html', {'form': form, 'page_title': 'Edit Industry'})


@login_required
@staff_required
def industry_delete(request, pk):
    industry = get_object_or_404(Industry, pk=pk)
    if request.method == 'POST':
        industry.delete()
        messages.success(request, 'Industry deleted.')
    return redirect('dashboard:industry_list')


# ---- Leadership CRUD ----
@login_required
@staff_required
def leadership_list(request):
    leaders = Leadership.objects.all()
    return render(request, 'dashboard/leadership/list.html', {'leaders': leaders, 'page_title': 'Leadership'})


@login_required
@staff_required
def leadership_create(request):
    from dashboard.forms import LeadershipForm
    if request.method == 'POST':
        form = LeadershipForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leader added.')
            return redirect('dashboard:leadership_list')
    else:
        form = LeadershipForm()
    return render(request, 'dashboard/leadership/form.html', {'form': form, 'page_title': 'Add Leader'})


@login_required
@staff_required
def leadership_edit(request, pk):
    from dashboard.forms import LeadershipForm
    leader = get_object_or_404(Leadership, pk=pk)
    if request.method == 'POST':
        form = LeadershipForm(request.POST, request.FILES, instance=leader)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leader updated.')
            return redirect('dashboard:leadership_list')
    else:
        form = LeadershipForm(instance=leader)
    return render(request, 'dashboard/leadership/form.html', {'form': form, 'page_title': 'Edit Leader'})


@login_required
@staff_required
def leadership_delete(request, pk):
    leader = get_object_or_404(Leadership, pk=pk)
    if request.method == 'POST':
        leader.delete()
        messages.success(request, 'Leader deleted.')
    return redirect('dashboard:leadership_list')


# ---- Blog CRUD ----
def _blog_filtered(request):
    from insights.models import BlogPost
    now = timezone.now()
    posts = BlogPost.objects.select_related('category', 'author')
    status = request.GET.get('status', '')
    cat = request.GET.get('category', '')
    q = request.GET.get('q', '').strip()[:100]
    sort = request.GET.get('sort', 'recent')
    if status == 'published':
        posts = posts.filter(is_published=True, published_at__lte=now)
    elif status == 'scheduled':
        posts = posts.filter(is_published=True, published_at__gt=now)
    elif status == 'draft':
        posts = posts.filter(is_published=False)
    elif status == 'featured':
        posts = posts.filter(is_featured=True)
    if cat.isdigit():
        posts = posts.filter(category_id=int(cat))
    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(excerpt__icontains=q) | Q(tags__icontains=q))
    order = {'recent': ['-updated_at'], 'views': ['-view_count'], 'published': ['-published_at'], 'title': ['title']}.get(sort, ['-updated_at'])
    return posts.order_by(*order), {'status': status, 'category': cat, 'q': q, 'sort': sort}


@login_required
@staff_required
def blog_list(request):
    from insights.models import BlogPost, BlogPostDailyView
    from django.db.models import Sum
    posts, f = _blog_filtered(request)
    if request.headers.get('x-requested-with') == 'fetch':
        html = render(request, 'dashboard/blog/_rows.html', {'posts': posts}).content.decode()
        return JsonResponse({'html': html, 'count': posts.count()})
    now = timezone.now()
    base = BlogPost.objects.all()
    stats = base.aggregate(
        total=Count('id'),
        published=Count('id', filter=Q(is_published=True, published_at__lte=now)),
        scheduled=Count('id', filter=Q(is_published=True, published_at__gt=now)),
        drafts=Count('id', filter=Q(is_published=False)),
        views=Sum('view_count'),
    )
    stats['views_30'] = BlogPostDailyView.objects.filter(date__gte=timezone.localdate() - timedelta(days=29)).aggregate(v=Sum('views'))['v'] or 0
    top = base.filter(is_published=True).order_by('-view_count').first()
    return render(request, 'dashboard/blog/list.html', {
        'posts': posts, 'filters': f, 'stats': stats, 'top_post': top,
        'categories': BlogCategory.objects.all(),
        'page_title': 'Blog Posts',
    })


def _blog_chart(post, days=30):
    from insights.models import BlogPostDailyView
    today = timezone.localdate()
    start = today - timedelta(days=days - 1)
    rows = dict(BlogPostDailyView.objects.filter(post=post, date__gte=start).values_list('date', 'views'))
    series = [{'date': start + timedelta(days=i), 'views': rows.get(start + timedelta(days=i), 0)} for i in range(days)]
    peak = max([d['views'] for d in series] + [1])
    for d in series:
        d['pct'] = round(100 * d['views'] / peak)
    return series, sum(d['views'] for d in series), peak


@login_required
@staff_required
def blog_view(request, pk):
    from insights.models import BlogPost
    post = get_object_or_404(BlogPost.objects.select_related('category', 'author'), pk=pk)
    series, views_30, peak = _blog_chart(post)
    newer = BlogPost.objects.filter(updated_at__gt=post.updated_at).order_by('updated_at').first()
    older = BlogPost.objects.filter(updated_at__lt=post.updated_at).order_by('-updated_at').first()
    return render(request, 'dashboard/blog/view.html', {
        'post': post, 'series': series, 'views_30': views_30, 'peak': peak,
        'newer': newer, 'older': older,
        'page_title': post.title,
    })


@login_required
@staff_required
def blog_toggle(request, pk):
    from insights.models import BlogPost
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        what = request.POST.get('field')
        if what == 'publish':
            post.is_published = not post.is_published
            if post.is_published and not post.published_at:
                post.published_at = timezone.now()
            post.save(update_fields=['is_published', 'published_at', 'updated_at'])
            messages.success(request, 'Post published.' if post.is_published else 'Post moved to drafts.')
        elif what == 'feature':
            post.is_featured = not post.is_featured
            post.save(update_fields=['is_featured', 'updated_at'])
            messages.success(request, 'Post featured on the Insights page.' if post.is_featured else 'Post is no longer featured.')
    nxt = request.POST.get('next') or ''
    if nxt.startswith('/admin-dashboard/'):
        return redirect(nxt)
    return redirect('dashboard:blog_view', pk=pk)


def _blog_save(request, form, creating):
    post = form.save(commit=False)
    if creating:
        post.author = request.user
    if post.is_published and not post.published_at:
        post.published_at = timezone.now()
    post.save()
    return post


@login_required
@staff_required
def blog_create(request):
    from dashboard.forms import BlogPostForm
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = _blog_save(request, form, True)
            messages.success(request, 'Post created.')
            if 'save_continue' in request.POST:
                return redirect('dashboard:blog_edit', pk=post.pk)
            return redirect('dashboard:blog_view', pk=post.pk)
        messages.error(request, 'Some fields need your attention.')
    else:
        form = BlogPostForm(initial={'is_published': False})
    return render(request, 'dashboard/blog/form.html', {'form': form, 'page_title': 'New Post'})


@login_required
@staff_required
def blog_edit(request, pk):
    from dashboard.forms import BlogPostForm
    from insights.models import BlogPost
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = _blog_save(request, form, False)
            messages.success(request, 'Post updated.')
            if 'save_continue' in request.POST:
                return redirect('dashboard:blog_edit', pk=post.pk)
            return redirect('dashboard:blog_view', pk=post.pk)
        messages.error(request, 'Some fields need your attention.')
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'dashboard/blog/form.html', {'form': form, 'page_title': f'Edit: {post.title}', 'post': post})


@login_required
@staff_required
def blog_delete(request, pk):
    from insights.models import BlogPost
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
    return redirect('dashboard:blog_list')


# ---- FAQ CRUD ----
@login_required
@staff_required
def faq_list(request):
    from core.models import FAQCategory
    faqs = list(FAQ.objects.select_related('category'))
    groups = []
    for cat in FAQCategory.objects.all():
        groups.append({'category': cat, 'faqs': [f for f in faqs if f.category_id == cat.pk]})
    loose = [f for f in faqs if not f.category_id]
    if loose:
        groups.append({'category': None, 'faqs': loose})
    votes_yes = sum(f.helpful_yes for f in faqs)
    votes = votes_yes + sum(f.helpful_no for f in faqs)
    return render(request, 'dashboard/faqs/list.html', {
        'groups': groups,
        'stats': {
            'total': len(faqs),
            'live': sum(1 for f in faqs if f.is_active),
            'hidden': sum(1 for f in faqs if not f.is_active),
            'popular': sum(1 for f in faqs if f.is_popular),
            'helpful': round(100 * votes_yes / votes) if votes else None,
            'votes': votes,
        },
        'page_title': 'FAQs',
    })


@login_required
@staff_required
def faq_view(request, pk):
    faq = get_object_or_404(FAQ.objects.select_related('category'), pk=pk)
    ordered = list(FAQ.objects.select_related('category').order_by(
        F('category__display_order').asc(nulls_last=True), 'category__name', 'display_order', 'pk').values_list('pk', flat=True))
    i = ordered.index(faq.pk)
    siblings = FAQ.objects.filter(category=faq.category).exclude(pk=faq.pk)[:5] if faq.category_id else []
    return render(request, 'dashboard/faqs/view.html', {
        'faq': faq,
        'prev_id': ordered[i - 1] if i > 0 else None,
        'next_id': ordered[i + 1] if i < len(ordered) - 1 else None,
        'position': i + 1, 'total': len(ordered),
        'siblings': siblings,
        'page_title': 'Question',
    })


def _faq_save(request, instance=None):
    from dashboard.forms import FAQForm
    initial = {}
    if not instance and request.GET.get('category'):
        initial['category'] = request.GET['category']
    form = FAQForm(request.POST or None, instance=instance, initial=initial)
    if request.method == 'POST' and form.is_valid():
        faq = form.save()
        messages.success(request, 'Question {}.'.format('updated' if instance else 'added'))
        if 'save_continue' in request.POST:
            return redirect('dashboard:faq_edit', pk=faq.pk)
        return redirect('dashboard:faq_view', pk=faq.pk)
    return render(request, 'dashboard/faqs/form.html', {
        'form': form, 'faq': instance,
        'page_title': 'Edit Question' if instance else 'Add Question',
    })


@login_required
@staff_required
def faq_create(request):
    return _faq_save(request)


@login_required
@staff_required
def faq_edit(request, pk):
    return _faq_save(request, get_object_or_404(FAQ, pk=pk))


@login_required
@staff_required
def faq_delete(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    if request.method == 'POST':
        faq.delete()
        messages.success(request, 'Question deleted.')
    return redirect('dashboard:faq_list')


@login_required
@staff_required
def faq_toggle(request, pk):
    """POST: flip 'is_active' or 'is_popular'. JSON for fetch(), redirect otherwise."""
    faq = get_object_or_404(FAQ, pk=pk)
    field = request.POST.get('field')
    if request.method == 'POST' and field in ('is_active', 'is_popular'):
        setattr(faq, field, not getattr(faq, field))
        faq.save(update_fields=[field, 'updated_at'])
    if request.headers.get('x-requested-with') == 'fetch':
        return JsonResponse({'ok': True, 'is_active': faq.is_active, 'is_popular': faq.is_popular})
    if request.POST.get('next') == 'view':
        messages.success(request, {'is_active': 'Shown on website.' if faq.is_active else 'Hidden from website.',
                                   'is_popular': 'Marked as popular.' if faq.is_popular else 'Removed from popular.'}.get(field, 'Saved.'))
        return redirect('dashboard:faq_view', pk=faq.pk)
    return redirect('dashboard:faq_list')


@login_required
@staff_required
def faq_reorder(request):
    """POST JSON {category: id|null, ids: [...]}: new order (and category) after a drag."""
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)
    try:
        data = json.loads(request.body)
        ids = [int(i) for i in data.get('ids', [])]
        cat = data.get('category')
        cat = int(cat) if cat not in (None, '', 'none') else None
    except (ValueError, TypeError):
        return JsonResponse({'ok': False}, status=400)
    for order, pk in enumerate(ids, start=1):
        FAQ.objects.filter(pk=pk).update(display_order=order, category_id=cat)
    return JsonResponse({'ok': True})


# ---- FAQ categories ----
@login_required
@staff_required
def faqcategory_list(request):
    from core.models import FAQCategory
    cats = FAQCategory.objects.annotate(
        total=Count('faqs'), live=Count('faqs', filter=Q(faqs__is_active=True)))
    return render(request, 'dashboard/faqs/categories.html', {'categories': cats, 'page_title': 'FAQ Topics'})


def _faqcategory_save(request, instance=None):
    from dashboard.forms import FAQCategoryForm
    form = FAQCategoryForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        cat = form.save()
        messages.success(request, f'Topic “{cat.name}” {"updated" if instance else "added"}.')
        return redirect('dashboard:faqcategory_list')
    return render(request, 'dashboard/faqs/category_form.html', {
        'form': form, 'category': instance,
        'page_title': 'Edit Topic' if instance else 'Add Topic',
    })


@login_required
@staff_required
def faqcategory_create(request):
    return _faqcategory_save(request)


@login_required
@staff_required
def faqcategory_edit(request, pk):
    from core.models import FAQCategory
    return _faqcategory_save(request, get_object_or_404(FAQCategory, pk=pk))


@login_required
@staff_required
def faqcategory_delete(request, pk):
    from core.models import FAQCategory
    cat = get_object_or_404(FAQCategory, pk=pk)
    if request.method == 'POST':
        name = cat.name
        cat.delete()
        messages.success(request, f'Topic “{name}” deleted. Its questions are kept under “No topic”.')
    return redirect('dashboard:faqcategory_list')


# ---- Contact Inquiries ----
@login_required
@staff_required
def inquiry_list(request):
    from django.core.paginator import Paginator
    base = ContactInquiry.objects.all()
    status_filter = request.GET.get('status', '')
    read_filter = request.GET.get('read', '')
    search = request.GET.get('q', '').strip()
    inquiries = base
    if status_filter in dict(ContactInquiry.STATUS_CHOICES):
        inquiries = inquiries.filter(status=status_filter)
    if read_filter == 'unread':
        inquiries = inquiries.filter(is_read=False)
    elif read_filter == 'read':
        inquiries = inquiries.filter(is_read=True)
    if search:
        inquiries = inquiries.filter(
            Q(name__icontains=search) | Q(email__icontains=search) | Q(company__icontains=search)
            | Q(phone__icontains=search) | Q(service__icontains=search) | Q(message__icontains=search)
        )
    week_ago = timezone.now() - timedelta(days=7)
    stats = base.aggregate(
        total=Count('id'),
        unread=Count('id', filter=Q(is_read=False)),
        open=Count('id', filter=Q(status__in=['new', 'contacted', 'in_progress'])),
        week=Count('id', filter=Q(created_at__gte=week_ago)),
    )
    page = Paginator(inquiries, 20).get_page(request.GET.get('page'))
    query = request.GET.copy()
    query.pop('page', None)
    return render(request, 'dashboard/inquiries/list.html', {
        'page_obj': page,
        'inquiries': page.object_list,
        'stats': stats,
        'page_title': 'Contact Inquiries',
        'status_filter': status_filter,
        'read_filter': read_filter,
        'search': search,
        'status_choices': ContactInquiry.STATUS_CHOICES,
        'query_string': query.urlencode(),
    })


def _wants_json(request):
    return request.headers.get('x-requested-with') == 'fetch'


@login_required
@staff_required
def inquiry_detail(request, pk):
    inquiry = get_object_or_404(ContactInquiry, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(ContactInquiry.STATUS_CHOICES):
            inquiry.status = new_status
        inquiry.admin_notes = request.POST.get('admin_notes', '')[:5000]
        inquiry.save()
        messages.success(request, 'Inquiry updated.')
        return redirect('dashboard:inquiry_detail', pk=pk)
    # Opening the full page marks it read (unless the admin just marked it unread)
    if not inquiry.is_read and request.GET.get('keep') != 'unread':
        inquiry.is_read = True
        inquiry.save(update_fields=['is_read', 'updated_at'])
    newer = ContactInquiry.objects.filter(created_at__gt=inquiry.created_at).order_by('created_at').first()
    older = ContactInquiry.objects.filter(created_at__lt=inquiry.created_at).order_by('-created_at').first()
    others = ContactInquiry.objects.filter(email__iexact=inquiry.email).exclude(pk=inquiry.pk)[:5]
    return render(request, 'dashboard/inquiries/detail.html', {
        'inquiry': inquiry,
        'newer': newer,
        'older': older,
        'others': others,
        'status_choices': ContactInquiry.STATUS_CHOICES,
        'page_title': f'Inquiry from {inquiry.name}',
    })


@login_required
@staff_required
def inquiry_toggle_read(request, pk):
    inquiry = get_object_or_404(ContactInquiry, pk=pk)
    if request.method == 'POST':
        state = request.POST.get('read')
        inquiry.is_read = (state == '1') if state in ('0', '1') else not inquiry.is_read
        inquiry.save(update_fields=['is_read', 'updated_at'])
    unread = ContactInquiry.objects.filter(is_read=False).count()
    if _wants_json(request):
        return JsonResponse({'ok': True, 'is_read': inquiry.is_read, 'unread': unread})
    messages.success(request, 'Marked as read.' if inquiry.is_read else 'Marked as unread.')
    nxt = request.POST.get('next') or ''
    if nxt.startswith('/admin-dashboard/'):
        return redirect(nxt)
    return redirect('dashboard:inquiry_list')


@login_required
@staff_required
def inquiry_bulk(request):
    if request.method != 'POST':
        return redirect('dashboard:inquiry_list')
    ids = [int(x) for x in request.POST.getlist('ids') if x.isdigit()]
    action = request.POST.get('action')
    qs = ContactInquiry.objects.filter(pk__in=ids)
    n = qs.count()
    if not n:
        messages.error(request, 'Select at least one inquiry.')
    elif action == 'read':
        qs.update(is_read=True)
        messages.success(request, f'{n} marked as read.')
    elif action == 'unread':
        qs.update(is_read=False)
        messages.success(request, f'{n} marked as unread.')
    elif action == 'delete':
        qs.delete()
        messages.success(request, f'{n} deleted.')
    elif action in dict(ContactInquiry.STATUS_CHOICES):
        qs.update(status=action)
        messages.success(request, f'{n} set to {dict(ContactInquiry.STATUS_CHOICES)[action]}.')
    nxt = request.POST.get('next') or ''
    return redirect(nxt if nxt.startswith('/admin-dashboard/') else 'dashboard:inquiry_list')


@login_required
@staff_required
def inquiry_delete(request, pk):
    inquiry = get_object_or_404(ContactInquiry, pk=pk)
    if request.method == 'POST':
        inquiry.delete()
        messages.success(request, 'Inquiry deleted.')
    return redirect('dashboard:inquiry_list')


# ---- Site Settings ----
@login_required
@staff_required
def site_settings_edit(request):
    from dashboard.forms import SiteSettingsForm
    settings_obj = SiteSettings.get_settings()
    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated.')
            return redirect('dashboard:site_settings')
    else:
        form = SiteSettingsForm(instance=settings_obj)
    return render(request, 'dashboard/settings.html', {'form': form, 'page_title': 'Site Settings'})


# ---- Pages CRUD ----
@login_required
@staff_required
def page_list(request):
    pages = Page.objects.all()
    return render(request, 'dashboard/pages/list.html', {'pages': pages, 'page_title': 'Pages'})


@login_required
@staff_required
def page_create(request):
    from dashboard.forms import PageForm
    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Page created.')
            return redirect('dashboard:page_list')
    else:
        form = PageForm()
    return render(request, 'dashboard/pages/form.html', {'form': form, 'page_title': 'New Page'})


@login_required
@staff_required
def page_edit(request, pk):
    from dashboard.forms import PageForm
    page = get_object_or_404(Page, pk=pk)
    if request.method == 'POST':
        form = PageForm(request.POST, request.FILES, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, 'Page updated.')
            nxt = request.POST.get('next') or request.GET.get('next') or ''
            return redirect(nxt if nxt.startswith('/admin-dashboard/') else 'dashboard:page_list')
    else:
        form = PageForm(instance=page)
    nxt = request.GET.get('next', '')
    return render(request, 'dashboard/pages/form.html', {
        'form': form, 'page_title': f'Edit {page.title}', 'page_obj': page,
        'next': nxt if nxt.startswith('/admin-dashboard/') else '',
    })


JOIN_US_PAGES = {
    'life-at-tm-solutech': {'title': 'Life at TM Solutech', 'icon': 'fas fa-people-group', 'blurb': 'Culture, people and what working here is like.'},
    'careers': {'title': 'Careers', 'icon': 'fas fa-briefcase', 'blurb': 'Open roles and how to apply.'},
}


@login_required
@staff_required
def joinus_page(request, slug):
    """Read-only view of a Join Us page (Life at TM Solutech / Careers)."""
    from django.utils.html import strip_tags
    if slug not in JOIN_US_PAGES:
        from django.http import Http404
        raise Http404
    meta = JOIN_US_PAGES[slug]
    page = Page.objects.filter(slug=slug).first()
    words = len(strip_tags(page.content or '').split()) if page else 0
    return render(request, 'dashboard/joinus/view.html', {
        'page': page, 'slug': slug, 'meta': meta, 'words': words,
        'read_minutes': max(1, round(words / 200)) if words else 0,
        'other': [(k, v) for k, v in JOIN_US_PAGES.items() if k != slug],
        'page_title': meta['title'],
    })


@login_required
@staff_required
def page_delete(request, pk):
    page = get_object_or_404(Page, pk=pk)
    if request.method == 'POST':
        page.delete()
        messages.success(request, 'Page deleted.')
    return redirect('dashboard:page_list')


# ---- Statistic CRUD ----
@login_required
@staff_required
def statistic_list(request):
    stats = Statistic.objects.all()
    return render(request, 'dashboard/statistics/list.html', {'stats': stats, 'page_title': 'Trust Bar Statistics'})


@login_required
@staff_required
def statistic_create(request):
    from dashboard.forms import StatisticForm
    if request.method == 'POST':
        form = StatisticForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Statistic added.')
            return redirect('dashboard:statistic_list')
    else:
        form = StatisticForm()
    return render(request, 'dashboard/statistics/form.html', {'form': form, 'page_title': 'Add Statistic'})


@login_required
@staff_required
def statistic_edit(request, pk):
    from dashboard.forms import StatisticForm
    stat = get_object_or_404(Statistic, pk=pk)
    if request.method == 'POST':
        form = StatisticForm(request.POST, instance=stat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Statistic updated.')
            return redirect('dashboard:statistic_list')
    else:
        form = StatisticForm(instance=stat)
    return render(request, 'dashboard/statistics/form.html', {'form': form, 'page_title': 'Edit Statistic'})


@login_required
@staff_required
def statistic_delete(request, pk):
    stat = get_object_or_404(Statistic, pk=pk)
    if request.method == 'POST':
        stat.delete()
        messages.success(request, 'Statistic deleted.')
    return redirect('dashboard:statistic_list')


# ---- WhyUsReason CRUD ----
@login_required
@staff_required
def whyus_list(request):
    reasons = WhyUsReason.objects.all()
    return render(request, 'dashboard/whyus/list.html', {'reasons': reasons, 'page_title': 'Why Choose Us'})


@login_required
@staff_required
def whyus_create(request):
    from dashboard.forms import WhyUsReasonForm
    if request.method == 'POST':
        form = WhyUsReasonForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reason added.')
            return redirect('dashboard:whyus_list')
    else:
        form = WhyUsReasonForm()
    return render(request, 'dashboard/whyus/form.html', {'form': form, 'page_title': 'Add Reason'})


@login_required
@staff_required
def whyus_edit(request, pk):
    from dashboard.forms import WhyUsReasonForm
    reason = get_object_or_404(WhyUsReason, pk=pk)
    if request.method == 'POST':
        form = WhyUsReasonForm(request.POST, request.FILES, instance=reason)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reason updated.')
            return redirect('dashboard:whyus_list')
    else:
        form = WhyUsReasonForm(instance=reason)
    return render(request, 'dashboard/whyus/form.html', {'form': form, 'page_title': 'Edit Reason'})


@login_required
@staff_required
def whyus_delete(request, pk):
    reason = get_object_or_404(WhyUsReason, pk=pk)
    if request.method == 'POST':
        reason.delete()
        messages.success(request, 'Reason deleted.')
    return redirect('dashboard:whyus_list')


# ---- BlogCategory CRUD ----
@login_required
@staff_required
def blogcategory_list(request):
    now = timezone.now()
    categories = BlogCategory.objects.annotate(
        live=Count('posts', filter=Q(posts__is_published=True, posts__published_at__lte=now)),
        total=Count('posts'),
        last_post=Max('posts__published_at', filter=Q(posts__is_published=True, posts__published_at__lte=now)),
    ).order_by('name')
    return render(request, 'dashboard/blogcategories/list.html', {
        'categories': categories,
        'shown': sum(1 for c in categories if c.is_active and c.live),
        'uncategorised': BlogPost.objects.filter(category__isnull=True).count(),
        'page_title': 'Blog Categories',
    })


@login_required
@staff_required
def blogcategory_create(request):
    from dashboard.forms import BlogCategoryForm
    if request.method == 'POST':
        form = BlogCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category “{category.name}” added.')
            return redirect('dashboard:blogcategory_list')
    else:
        form = BlogCategoryForm()
    return render(request, 'dashboard/blogcategories/form.html', {'form': form, 'page_title': 'Add Category'})


@login_required
@staff_required
def blogcategory_edit(request, pk):
    from dashboard.forms import BlogCategoryForm
    category = get_object_or_404(BlogCategory, pk=pk)
    if request.method == 'POST':
        form = BlogCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category “{category.name}” updated.')
            return redirect('dashboard:blogcategory_list')
    else:
        form = BlogCategoryForm(instance=category)
    return render(request, 'dashboard/blogcategories/form.html', {'form': form, 'category': category, 'page_title': 'Edit Category'})


@login_required
@staff_required
def blogcategory_delete(request, pk):
    category = get_object_or_404(BlogCategory, pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category “{name}” deleted. Its articles are kept without a category.')
    return redirect('dashboard:blogcategory_list')


# ---- Our Work (case studies) ----
@login_required
@staff_required
def work_list(request):
    from work.models import CaseStudy
    cases = CaseStudy.objects.select_related('industry', 'service')
    return render(request, 'dashboard/work/list.html', {
        'cases': cases,
        'stats': {
            'total': len(cases),
            'published': sum(1 for c in cases if c.is_published),
            'drafts': sum(1 for c in cases if not c.is_published),
            'industries': len({c.industry_id for c in cases if c.industry_id and c.is_published}),
        },
        'page_title': 'Case Studies',
    })


def _work_save(request, instance=None):
    from dashboard.forms import CaseStudyForm
    form = CaseStudyForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        case = form.save()
        if case.is_featured:
            type(case).objects.exclude(pk=case.pk).filter(is_featured=True).update(is_featured=False)
        messages.success(request, f'“{case.title}” {"updated" if instance else "added"}.')
        if 'save_continue' in request.POST:
            return redirect('dashboard:work_edit', pk=case.pk)
        return redirect('dashboard:work_list')
    return render(request, 'dashboard/work/form.html', {
        'form': form, 'case': instance,
        'page_title': 'Edit Case Study' if instance else 'Add Case Study',
    })


@login_required
@staff_required
def work_create(request):
    return _work_save(request)


@login_required
@staff_required
def work_edit(request, pk):
    from work.models import CaseStudy
    return _work_save(request, get_object_or_404(CaseStudy, pk=pk))


@login_required
@staff_required
def work_delete(request, pk):
    from work.models import CaseStudy
    case = get_object_or_404(CaseStudy, pk=pk)
    if request.method == 'POST':
        title = case.title
        case.delete()
        messages.success(request, f'“{title}” deleted.')
    return redirect('dashboard:work_list')


# ---- Capability CRUD ----
@login_required
@staff_required
def capability_list(request):
    capabilities = Capability.objects.all()
    return render(request, 'dashboard/capabilities/list.html', {'capabilities': capabilities, 'page_title': 'Capabilities'})


@login_required
@staff_required
def capability_create(request):
    from dashboard.forms import CapabilityForm
    if request.method == 'POST':
        form = CapabilityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Capability added.')
            return redirect('dashboard:capability_list')
    else:
        form = CapabilityForm()
    return render(request, 'dashboard/capabilities/form.html', {'form': form, 'page_title': 'Add Capability'})


@login_required
@staff_required
def capability_edit(request, pk):
    from dashboard.forms import CapabilityForm
    capability = get_object_or_404(Capability, pk=pk)
    if request.method == 'POST':
        form = CapabilityForm(request.POST, instance=capability)
        if form.is_valid():
            form.save()
            messages.success(request, 'Capability updated.')
            return redirect('dashboard:capability_list')
    else:
        form = CapabilityForm(instance=capability)
    return render(request, 'dashboard/capabilities/form.html', {'form': form, 'page_title': 'Edit Capability'})


@login_required
@staff_required
def capability_delete(request, pk):
    capability = get_object_or_404(Capability, pk=pk)
    if request.method == 'POST':
        capability.delete()
        messages.success(request, 'Capability deleted.')
    return redirect('dashboard:capability_list')


# ---- ClientLogo CRUD ----
@login_required
@staff_required
def clientlogo_list(request):
    logos = ClientLogo.objects.all()
    return render(request, 'dashboard/clientlogos/list.html', {
        'logos': logos,
        'live': sum(1 for l in logos if l.is_active),
        'unnamed': sum(1 for l in logos if l.name.startswith('Client ')),
        'page_title': 'Clients',
    })


@login_required
@staff_required
def clientlogo_create(request):
    from dashboard.forms import ClientLogoForm
    if request.method == 'POST':
        form = ClientLogoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client added.')
            return redirect('dashboard:clientlogo_list')
    else:
        form = ClientLogoForm()
    return render(request, 'dashboard/clientlogos/form.html', {'form': form, 'page_title': 'Add Client'})


@login_required
@staff_required
def clientlogo_edit(request, pk):
    from dashboard.forms import ClientLogoForm
    logo = get_object_or_404(ClientLogo, pk=pk)
    if request.method == 'POST':
        form = ClientLogoForm(request.POST, request.FILES, instance=logo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client updated.')
            return redirect('dashboard:clientlogo_list')
    else:
        form = ClientLogoForm(instance=logo)
    return render(request, 'dashboard/clientlogos/form.html', {'form': form, 'client': logo, 'page_title': 'Edit Client'})


@login_required
@staff_required
def clientlogo_delete(request, pk):
    logo = get_object_or_404(ClientLogo, pk=pk)
    if request.method == 'POST':
        logo.delete()
        messages.success(request, 'Logo deleted.')
    return redirect('dashboard:clientlogo_list')


# ---- HeroTag CRUD ----
@login_required
@staff_required
def herotag_list(request):
    tags = HeroTag.objects.all()
    return render(request, 'dashboard/herotags/list.html', {'tags': tags, 'page_title': 'Hero Tags'})


@login_required
@staff_required
def herotag_create(request):
    from dashboard.forms import HeroTagForm
    if request.method == 'POST':
        form = HeroTagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tag added.')
            return redirect('dashboard:herotag_list')
    else:
        form = HeroTagForm()
    return render(request, 'dashboard/herotags/form.html', {'form': form, 'page_title': 'Add Hero Tag'})


@login_required
@staff_required
def herotag_edit(request, pk):
    from dashboard.forms import HeroTagForm
    tag = get_object_or_404(HeroTag, pk=pk)
    if request.method == 'POST':
        form = HeroTagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tag updated.')
            return redirect('dashboard:herotag_list')
    else:
        form = HeroTagForm(instance=tag)
    return render(request, 'dashboard/herotags/form.html', {'form': form, 'page_title': 'Edit Hero Tag'})


@login_required
@staff_required
def herotag_delete(request, pk):
    tag = get_object_or_404(HeroTag, pk=pk)
    if request.method == 'POST':
        tag.delete()
        messages.success(request, 'Tag deleted.')
    return redirect('dashboard:herotag_list')


# ---- HeroSlide CRUD (homepage carousel) ----
@login_required
@staff_required
def heroslide_list(request):
    slides = HeroSlide.objects.all()
    return render(request, 'dashboard/heroslides/list.html', {'slides': slides, 'page_title': 'Hero Slides'})


@login_required
@staff_required
def heroslide_create(request):
    from dashboard.forms import HeroSlideForm
    if request.method == 'POST':
        form = HeroSlideForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Slide added.')
            return redirect('dashboard:heroslide_list')
    else:
        form = HeroSlideForm(initial={'display_order': HeroSlide.objects.count() + 1})
    return render(request, 'dashboard/heroslides/form.html', {'form': form, 'page_title': 'Add Hero Slide'})


@login_required
@staff_required
def heroslide_edit(request, pk):
    from dashboard.forms import HeroSlideForm
    slide = get_object_or_404(HeroSlide, pk=pk)
    if request.method == 'POST':
        form = HeroSlideForm(request.POST, request.FILES, instance=slide)
        if form.is_valid():
            form.save()
            messages.success(request, 'Slide updated.')
            return redirect('dashboard:heroslide_list')
    else:
        form = HeroSlideForm(instance=slide)
    return render(request, 'dashboard/heroslides/form.html', {'form': form, 'slide': slide, 'page_title': 'Edit Hero Slide'})


@login_required
@staff_required
def heroslide_delete(request, pk):
    slide = get_object_or_404(HeroSlide, pk=pk)
    if request.method == 'POST':
        slide.delete()
        messages.success(request, 'Slide deleted.')
    return redirect('dashboard:heroslide_list')


# ---- HeroStat CRUD ----
@login_required
@staff_required
def herostat_list(request):
    stats = HeroStat.objects.all()
    return render(request, 'dashboard/herostats/list.html', {'stats': stats, 'page_title': 'Hero Floating Stats'})


@login_required
@staff_required
def herostat_create(request):
    from dashboard.forms import HeroStatForm
    if request.method == 'POST':
        form = HeroStatForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stat added.')
            return redirect('dashboard:herostat_list')
    else:
        form = HeroStatForm()
    return render(request, 'dashboard/herostats/form.html', {'form': form, 'page_title': 'Add Hero Stat'})


@login_required
@staff_required
def herostat_edit(request, pk):
    from dashboard.forms import HeroStatForm
    stat = get_object_or_404(HeroStat, pk=pk)
    if request.method == 'POST':
        form = HeroStatForm(request.POST, instance=stat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stat updated.')
            return redirect('dashboard:herostat_list')
    else:
        form = HeroStatForm(instance=stat)
    return render(request, 'dashboard/herostats/form.html', {'form': form, 'page_title': 'Edit Hero Stat'})


@login_required
@staff_required
def herostat_delete(request, pk):
    stat = get_object_or_404(HeroStat, pk=pk)
    if request.method == 'POST':
        stat.delete()
        messages.success(request, 'Stat deleted.')
    return redirect('dashboard:herostat_list')


# ==========================================================================
# NAVBAR → SERVICES MENU
# Manages which service categories/services appear in the site's Services
# mega-menu, their order, navbar labels, descriptions and badges.
# ==========================================================================

def _unique_slug(model, value):
    from django.utils.text import slugify
    base = slugify(value)[:180] or 'item'
    slug, n = base, 2
    while model.objects.filter(slug=slug).exists():
        slug = f'{base}-{n}'
        n += 1
    return slug


@login_required
@staff_required
def navbar_services(request):
    categories = ServiceCategory.objects.prefetch_related(
        Prefetch('services', queryset=Service.objects.order_by('display_order'))
    ).order_by('display_order')
    in_nav = Service.objects.filter(is_active=True, show_in_nav=True, category__is_active=True, category__show_in_nav=True).count()
    context = {
        'categories': categories,
        'badge_choices': Service.NAV_BADGE_CHOICES,
        'nav_service_total': in_nav,
        'nav_category_total': ServiceCategory.objects.filter(is_active=True, show_in_nav=True).count(),
        'page_title': 'Navbar · Services Menu',
    }
    return render(request, 'dashboard/navbar/services.html', context)


@login_required
@staff_required
def navbar_services_update(request):
    """JSON endpoint for drag-reorder, visibility toggles, badges and navbar text."""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body or '{}')
    except ValueError:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    action = data.get('action')
    models_by_kind = {'category': ServiceCategory, 'service': Service}

    if action == 'reorder_categories':
        ids = [int(i) for i in data.get('ids', [])]
        for order, pk in enumerate(ids, start=1):
            ServiceCategory.objects.filter(pk=pk).update(display_order=order)
        return JsonResponse({'ok': True})

    if action == 'reorder_services':
        category = get_object_or_404(ServiceCategory, pk=data.get('category_id'))
        ids = [int(i) for i in data.get('ids', [])]
        for order, pk in enumerate(ids, start=1):
            # Moving a service into another category is allowed (drag across groups)
            Service.objects.filter(pk=pk).update(display_order=order, category=category)
        return JsonResponse({'ok': True})

    model = models_by_kind.get(data.get('kind'))
    if model is None:
        return JsonResponse({'ok': False, 'error': 'Unknown item type'}, status=400)
    obj = get_object_or_404(model, pk=data.get('id'))

    if action == 'toggle':
        field = data.get('field')
        if field not in ('show_in_nav', 'is_active'):
            return JsonResponse({'ok': False, 'error': 'Field not allowed'}, status=400)
        setattr(obj, field, bool(data.get('value')))
        obj.save(update_fields=[field])
        return JsonResponse({'ok': True, 'value': getattr(obj, field)})

    if action == 'badge' and model is Service:
        badge = data.get('badge', '')
        if badge not in dict(Service.NAV_BADGE_CHOICES):
            return JsonResponse({'ok': False, 'error': 'Invalid badge'}, status=400)
        obj.nav_badge = badge
        obj.save(update_fields=['nav_badge'])
        return JsonResponse({'ok': True})

    return JsonResponse({'ok': False, 'error': 'Unknown action'}, status=400)


# ---- Contact page settings ----
@login_required
@staff_required
def contact_page_view(request):
    """Read-only overview of everything on the public Contact page."""
    from django.conf import settings as dj_settings
    from contact.models import ContactPageSettings
    from core.models import SocialLink
    cp = ContactPageSettings.get()
    return render(request, 'dashboard/contactpage/view.html', {
        'cp': cp,
        'sections_visible': 2 + sum([cp.show_details, cp.show_socials, cp.show_map]),
        'site': SiteSettings.get_settings(),
        'socials': SocialLink.objects.filter(is_active=True, show_on_contact=True),
        'default_inbox': dj_settings.ADMIN_EMAIL,
        'month_enquiries': ContactInquiry.objects.filter(created_at__gte=timezone.now() - timedelta(days=30)).count(),
        'awaiting': ContactInquiry.objects.filter(status='new').count(),
        'page_title': 'Contact Page',
    })


@login_required
@staff_required
def contact_page_edit(request):
    from contact.models import ContactPageSettings
    from dashboard.forms import ContactPageSettingsForm
    page = ContactPageSettings.get()
    if request.method == 'POST':
        form = ContactPageSettingsForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact page updated.')
            return redirect('dashboard:contact_page')
        messages.error(request, 'Some fields need your attention.')
    else:
        form = ContactPageSettingsForm(instance=page)
    return render(request, 'dashboard/contactpage/form.html', {'form': form, 'page_title': 'Contact Page'})


# ---- Social links ----
@login_required
@staff_required
def social_list(request):
    from contact.models import ContactPageSettings
    from core.models import SocialLink
    if request.method == 'POST' and request.POST.get('order'):
        # Drag-to-reorder: "3,1,2"
        ids = [int(x) for x in request.POST['order'].split(',') if x.isdigit()]
        for position, pk in enumerate(ids, start=1):
            SocialLink.objects.filter(pk=pk).update(display_order=position)
        messages.success(request, 'Order saved.')
        return redirect('dashboard:social_list')
    links = list(SocialLink.objects.all())
    live = [l for l in links if l.is_active]
    return render(request, 'dashboard/socials/list.html', {
        'links': links,
        'footer_links': [l for l in live if l.show_in_footer],
        'contact_links': [l for l in live if l.show_on_contact],
        'stats': {
            'total': len(links),
            'live': len(live),
            'footer': sum(1 for l in live if l.show_in_footer),
            'contact': sum(1 for l in live if l.show_on_contact),
        },
        'site': SiteSettings.get_settings(),
        'socials_title': ContactPageSettings.get().socials_title,
        'page_title': 'Social Links',
    })


@login_required
@staff_required
def social_create(request):
    from core.models import SocialLink
    from dashboard.forms import SocialLinkForm
    if request.method == 'POST':
        form = SocialLinkForm(request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            if not link.display_order:
                link.display_order = (SocialLink.objects.aggregate(m=Max('display_order'))['m'] or 0) + 1
            link.save()
            messages.success(request, f'{link.display_label} added.')
            return redirect('dashboard:social_list')
    else:
        form = SocialLinkForm()
    return render(request, 'dashboard/socials/form.html', {'form': form, 'page_title': 'Add Social Link', 'platforms': SocialLink.PLATFORMS})


@login_required
@staff_required
def social_edit(request, pk):
    from core.models import SocialLink
    from dashboard.forms import SocialLinkForm
    link = get_object_or_404(SocialLink, pk=pk)
    if request.method == 'POST':
        form = SocialLinkForm(request.POST, instance=link)
        if form.is_valid():
            form.save()
            messages.success(request, f'{link.display_label} updated.')
            return redirect('dashboard:social_list')
    else:
        form = SocialLinkForm(instance=link)
    return render(request, 'dashboard/socials/form.html', {'form': form, 'link': link, 'page_title': 'Edit Social Link', 'platforms': SocialLink.PLATFORMS})


@login_required
@staff_required
def social_delete(request, pk):
    from core.models import SocialLink
    link = get_object_or_404(SocialLink, pk=pk)
    if request.method == 'POST':
        label = link.display_label
        link.delete()
        messages.success(request, f'{label} removed.')
    return redirect('dashboard:social_list')
