from django.contrib import admin
from .models import BlogCategory, BlogPost


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_published', 'is_featured', 'published_at')
    list_filter = ('is_published', 'is_featured', 'category')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'excerpt')
    date_hierarchy = 'created_at'
