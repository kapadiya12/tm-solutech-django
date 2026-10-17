from django.contrib import admin
from django.db.models import Count, Q
from .models import ServiceCategory, Service, Industry


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'live_services', 'slug', 'is_active', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'display_order')
    ordering = ('display_order',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            live_count=Count('services', filter=Q(services__is_active=True))
        )

    @admin.display(description='Live services', ordering='live_count')
    def live_services(self, obj):
        return obj.live_count


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_featured', 'is_active', 'show_in_nav', 'display_order')
    list_select_related = ('category',)
    ordering = ('category__display_order', 'display_order')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('category', 'is_featured', 'is_active', 'show_in_nav')
    list_editable = ('is_featured', 'is_active', 'display_order')
    search_fields = ('title', 'short_description')


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'display_order')
