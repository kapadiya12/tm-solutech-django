def dashboard_counts(request):
    """Unread-inquiry badge for the dashboard sidebar (only queried on dashboard pages)."""
    if not request.path.startswith('/admin-dashboard/') or not getattr(request, 'user', None) or not request.user.is_staff:
        return {}
    from contact.models import ContactInquiry
    return {'new_inquiry_count': ContactInquiry.objects.filter(is_read=False).count()}
