from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.utils import timezone
from django.db import models
from .models import BlogPost, BlogCategory


def post_list(request):
    posts = BlogPost.objects.filter(
        is_published=True,
        published_at__lte=timezone.now()
    ).select_related('category', 'author')
    
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q', '').strip()
    
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    if search_query:
        posts = posts.filter(
            models.Q(title__icontains=search_query) | 
            models.Q(excerpt__icontains=search_query)
        )
    
    featured = posts.filter(is_featured=True).first()
    paginator = Paginator(posts, 9)
    page = request.GET.get('page')
    posts_page = paginator.get_page(page)
    
    categories = BlogCategory.objects.filter(is_active=True)
    
    context = {
        'posts': posts_page,
        'featured_post': featured,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
        'page_title': 'Latest Insights',
        'page_subtitle': 'Stay informed with the latest trends and insights in IT solutions',
    }
    return render(request, 'insights/post_list.html', context)


def post_detail(request, slug):
    post = get_object_or_404(
        BlogPost.objects.select_related('category', 'author'),
        slug=slug,
        is_published=True,
        published_at__lte=timezone.now()
    )
    related_posts = post.get_related_posts()
    context = {
        'post': post,
        'related_posts': related_posts,
        'page_title': post.title,
    }
    return render(request, 'insights/post_detail.html', context)
