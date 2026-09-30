from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from django.core.management import call_command
import io
import json

from core.models import (
    SiteSettings, Statistic, WhyUsReason, Testimonial, Leadership, FAQ, SEOSettings, Gallery,
    Capability, ClientLogo, HeroTag, HeroStat,
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
    One-click 'migrate' for hosts (like Render's free tier) with no shell
    access. Runs in-process, in the exact same environment/filesystem that
    serves the live site, so it's more reliable here than trying to get a
    platform's Build Command configured correctly.
    """
    output = None
    error = None
    if request.method == 'POST':
        buffer = io.StringIO()
        try:
            call_command('migrate', interactive=False, stdout=buffer, stderr=buffer)
            output = buffer.getvalue()
            messages.success(request, 'Migrations ran successfully.')
        except Exception as e:
            error = f"{buffer.getvalue()}\n{e}"
            messages.error(request, 'Migration failed — see details below.')
    return render(request, 'dashboard/run_migrations.html', {
        'page_title': 'Run Migrations',
        'output': output,
        'error': error,
    })


@login_required
@staff_required
def dashboard_index(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    
    context = {
        'total_services': Service.objects.filter(is_active=True).count(),
        'total_posts': BlogPost.objects.count(),
        'published_posts': BlogPost.objects.filter(is_published=True).count(),
        'total_inquiries': ContactInquiry.objects.count(),
        'new_inquiries': ContactInquiry.objects.filter(status='new').count(),
        'total_industries': Industry.objects.filter(is_active=True).count(),
        'total_leadership': Leadership.objects.filter(is_active=True).count(),
        'recent_inquiries': ContactInquiry.objects.order_by('-created_at')[:5],
        'recent_posts': BlogPost.objects.order_by('-created_at')[:5],
        'page_title': 'Dashboard',
    }
    
    # Chart data - inquiries over months
    inquiry_data = (
        ContactInquiry.objects
        .filter(created_at__gte=now - timedelta(days=180))
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    context['inquiry_chart_labels'] = json.dumps([d['month'].strftime('%b %Y') for d in inquiry_data])
    context['inquiry_chart_data'] = json.dumps([d['count'] for d in inquiry_data])
    
    # Status distribution
    status_data = (
        ContactInquiry.objects
        .values('status')
        .annotate(count=Count('id'))
    )
    context['status_labels'] = json.dumps([d['status'].title() for d in status_data])
    context['status_data'] = json.dumps([d['count'] for d in status_data])
    
    return render(request, 'dashboard/index.html', context)


# ---- Services CRUD ----
@login_required
@staff_required
def service_list(request):
    services = Service.objects.select_related('category').all()
    categories = ServiceCategory.objects.all()
    context = {
        'services': services,
        'categories': categories,
        'page_title': 'Manage Services',
    }
    return render(request, 'dashboard/services/list.html', context)


@login_required
@staff_required
def service_create(request):
    from dashboard.forms import ServiceForm
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service created successfully.')
            return redirect('dashboard:service_list')
    else:
        form = ServiceForm()
    return render(request, 'dashboard/services/form.html', {'form': form, 'page_title': 'Add Service'})


@login_required
@staff_required
def service_edit(request, pk):
    from dashboard.forms import ServiceForm
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully.')
            return redirect('dashboard:service_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'dashboard/services/form.html', {'form': form, 'page_title': 'Edit Service', 'service': service})


@login_required
@staff_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully.')
    return redirect('dashboard:service_list')


# ---- Category CRUD ----
@login_required
@staff_required
def category_list(request):
    categories = ServiceCategory.objects.annotate(service_count=Count('services'))
    return render(request, 'dashboard/categories/list.html', {'categories': categories, 'page_title': 'Service Categories'})


@login_required
@staff_required
def category_create(request):
    from dashboard.forms import ServiceCategoryForm
    if request.method == 'POST':
        form = ServiceCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully.')
            return redirect('dashboard:category_list')
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
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('dashboard:category_list')
    else:
        form = ServiceCategoryForm(instance=category)
    return render(request, 'dashboard/categories/form.html', {'form': form, 'page_title': 'Edit Category'})


@login_required
@staff_required
def category_delete(request, pk):
    category = get_object_or_404(ServiceCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
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
