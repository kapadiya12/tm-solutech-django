from django.shortcuts import get_object_or_404, render

from .models import CaseStudy


def _live():
    return CaseStudy.objects.filter(is_published=True).select_related('industry', 'service', 'service__category')


def work_list(request):
    cases = list(_live())
    featured = next((c for c in cases if c.is_featured), cases[0] if cases else None)
    industries = []
    for c in cases:
        if c.industry and c.industry not in industries:
            industries.append(c.industry)
    return render(request, 'work/list.html', {
        'featured': featured,
        'cases': [c for c in cases if c != featured],
        'count': len(cases),
        'industries': industries,
        'page_title': 'Our Work',
    })


def work_detail(request, slug):
    case = get_object_or_404(_live(), slug=slug)
    more = _live().exclude(pk=case.pk)
    if case.industry_id:
        more = sorted(more, key=lambda c: c.industry_id != case.industry_id)
    return render(request, 'work/detail.html', {
        'case': case,
        'more': list(more)[:3],
        'page_title': case.title,
    })
