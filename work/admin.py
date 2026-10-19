from django.contrib import admin

from .models import CaseStudy


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('title', 'client_name', 'industry', 'is_published', 'is_featured', 'order')
    list_filter = ('is_published', 'industry')
    prepopulated_fields = {'slug': ('title',)}
