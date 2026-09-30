from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Prefetch, Q
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
@login_required
@staff_required
def blog_list(request):
    posts = BlogPost.objects.select_related('category', 'author').all()
    return render(request, 'dashboard/blog/list.html', {'posts': posts, 'page_title': 'Blog Posts'})


@login_required
@staff_required
def blog_create(request):
    from dashboard.forms import BlogPostForm
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if post.is_published and not post.published_at:
                post.published_at = timezone.now()
            post.save()
            messages.success(request, 'Post created.')
            return redirect('dashboard:blog_list')
    else:
        form = BlogPostForm()
    return render(request, 'dashboard/blog/form.html', {'form': form, 'page_title': 'New Post'})


@login_required
@staff_required
def blog_edit(request, pk):
    from dashboard.forms import BlogPostForm
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            if post.is_published and not post.published_at:
                post.published_at = timezone.now()
            post.save()
            messages.success(request, 'Post updated.')
            return redirect('dashboard:blog_list')
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'dashboard/blog/form.html', {'form': form, 'page_title': 'Edit Post', 'post': post})


@login_required
@staff_required
def blog_delete(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
    return redirect('dashboard:blog_list')


# ---- FAQ CRUD ----
@login_required
@staff_required
def faq_list(request):
    faqs = FAQ.objects.all()
    return render(request, 'dashboard/faqs/list.html', {'faqs': faqs, 'page_title': 'FAQs'})


@login_required
@staff_required
def faq_create(request):
    from dashboard.forms import FAQForm
    if request.method == 'POST':
        form = FAQForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'FAQ created.')
            return redirect('dashboard:faq_list')
    else:
        form = FAQForm()
    return render(request, 'dashboard/faqs/form.html', {'form': form, 'page_title': 'Add FAQ'})


@login_required
@staff_required
def faq_edit(request, pk):
    from dashboard.forms import FAQForm
    faq = get_object_or_404(FAQ, pk=pk)
    if request.method == 'POST':
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            messages.success(request, 'FAQ updated.')
            return redirect('dashboard:faq_list')
    else:
        form = FAQForm(instance=faq)
    return render(request, 'dashboard/faqs/form.html', {'form': form, 'page_title': 'Edit FAQ'})


@login_required
@staff_required
def faq_delete(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    if request.method == 'POST':
        faq.delete()
        messages.success(request, 'FAQ deleted.')
    return redirect('dashboard:faq_list')


# ---- Contact Inquiries ----
@login_required
@staff_required
def inquiry_list(request):
    inquiries = ContactInquiry.objects.all()
    status_filter = request.GET.get('status', '')
    search = request.GET.get('q', '')
    if status_filter:
        inquiries = inquiries.filter(status=status_filter)
    if search:
        inquiries = inquiries.filter(
            Q(name__icontains=search) | Q(email__icontains=search) | Q(company__icontains=search)
        )
    return render(request, 'dashboard/inquiries/list.html', {
        'inquiries': inquiries,
        'page_title': 'Contact Inquiries',
        'status_filter': status_filter,
        'search': search,
    })


@login_required
@staff_required
def inquiry_detail(request, pk):
    inquiry = get_object_or_404(ContactInquiry, pk=pk)
    if not inquiry.is_read:
        inquiry.is_read = True
        inquiry.save()
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('admin_notes', '')
        if new_status:
            inquiry.status = new_status
        inquiry.admin_notes = notes
        inquiry.save()
        messages.success(request, 'Inquiry updated.')
        return redirect('dashboard:inquiry_detail', pk=pk)
    return render(request, 'dashboard/inquiries/detail.html', {'inquiry': inquiry, 'page_title': 'Inquiry Detail'})


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
            return redirect('dashboard:page_list')
    else:
        form = PageForm(instance=page)
    return render(request, 'dashboard/pages/form.html', {'form': form, 'page_title': 'Edit Page', 'page_obj': page})


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
    categories = BlogCategory.objects.all()
    return render(request, 'dashboard/blogcategories/list.html', {'categories': categories, 'page_title': 'Blog Categories'})


@login_required
@staff_required
def blogcategory_create(request):
    from dashboard.forms import BlogCategoryForm
    if request.method == 'POST':
        form = BlogCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added.')
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
            messages.success(request, 'Category updated.')
            return redirect('dashboard:blogcategory_list')
    else:
        form = BlogCategoryForm(instance=category)
    return render(request, 'dashboard/blogcategories/form.html', {'form': form, 'page_title': 'Edit Category'})


@login_required
@staff_required
def blogcategory_delete(request, pk):
    category = get_object_or_404(BlogCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted.')
    return redirect('dashboard:blogcategory_list')


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
    return render(request, 'dashboard/clientlogos/list.html', {'logos': logos, 'page_title': 'Client Logos'})


@login_required
@staff_required
def clientlogo_create(request):
    from dashboard.forms import ClientLogoForm
    if request.method == 'POST':
        form = ClientLogoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Logo added.')
            return redirect('dashboard:clientlogo_list')
    else:
        form = ClientLogoForm()
    return render(request, 'dashboard/clientlogos/form.html', {'form': form, 'page_title': 'Add Client Logo'})


@login_required
@staff_required
def clientlogo_edit(request, pk):
    from dashboard.forms import ClientLogoForm
    logo = get_object_or_404(ClientLogo, pk=pk)
    if request.method == 'POST':
        form = ClientLogoForm(request.POST, request.FILES, instance=logo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Logo updated.')
            return redirect('dashboard:clientlogo_list')
    else:
        form = ClientLogoForm(instance=logo)
    return render(request, 'dashboard/clientlogos/form.html', {'form': form, 'page_title': 'Edit Client Logo'})


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
