from django.contrib import admin
from .models import SiteSettings, Statistic, WhyUsReason, Testimonial, Gallery, SEOSettings, Leadership, FAQ, HeroSlide


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Company Info', {'fields': ('company_name', 'tagline', 'logo', 'favicon')}),
        ('Contact', {'fields': ('phone', 'email', 'address', 'google_maps_url', 'google_maps_embed')}),
        ('Social Media', {'fields': ('linkedin_url', 'facebook_url', 'instagram_url', 'youtube_url', 'whatsapp_number')}),
        ('Footer', {'fields': ('footer_description', 'copyright_text')}),
        ('SEO', {'fields': ('meta_title', 'meta_description', 'meta_keywords', 'og_image')}),
        ('Scripts', {'fields': ('header_scripts', 'footer_scripts'), 'classes': ('collapse',)}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'suffix', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    ordering = ('display_order',)


@admin.register(WhyUsReason)
class WhyUsReasonAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'rating', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')


@admin.register(SEOSettings)
class SEOSettingsAdmin(admin.ModelAdmin):
    list_display = ('page_name', 'meta_title')


@admin.register(Leadership)
class LeadershipAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    ordering = ('display_order',)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    list_filter = ('category',)
    ordering = ('display_order',)


# Customize Django Admin
admin.site.site_header = 'TM Solutech Admin'
admin.site.site_title = 'TM Solutech Administration'
admin.site.index_title = 'Administration Dashboard'


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('tab_label', 'title', 'accent', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    ordering = ('display_order',)
