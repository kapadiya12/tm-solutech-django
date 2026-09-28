from django.contrib import admin
from .models import Page


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'show_in_footer', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('is_published', 'show_in_footer')
    search_fields = ('title', 'content')
