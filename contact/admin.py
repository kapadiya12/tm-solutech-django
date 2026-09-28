from django.contrib import admin
from .models import ContactInquiry


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'service', 'status', 'is_read', 'created_at')
    list_filter = ('status', 'is_read', 'created_at')
    search_fields = ('name', 'email', 'company', 'message')
    readonly_fields = ('name', 'company', 'email', 'phone', 'subject', 'service', 'message', 'created_at')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
