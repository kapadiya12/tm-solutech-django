from django.shortcuts import render, get_object_or_404
from .models import Page


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_published=True)
    context = {
        'page': page,
        'page_title': page.title,
    }
    return render(request, 'cms/page_detail.html', context)
