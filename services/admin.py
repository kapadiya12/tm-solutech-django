from django.contrib import admin
from .models import ServiceCategory, Service, Industry


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'display_order')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_featured', 'is_active', 'display_order')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('category', 'is_featured', 'is_active')
    list_editable = ('is_featured', 'is_active', 'display_order')
    search_fields = ('title', 'short_description')


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'display_order')
