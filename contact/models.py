import datetime

from django.db import models


class ContactInquiry(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    name = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=300, blank=True)
    service = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    is_read = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Inquiry'
        verbose_name_plural = 'Contact Inquiries'

    def __str__(self):
        return f"{self.name} - {self.subject or 'No Subject'}"


def default_reply_steps():
    return [
        {'title': 'We review your message', 'text': 'and what you need.'},
        {'title': 'We get in touch', 'text': 'by email or phone within 1–2 business days.'},
        {'title': 'We plan the next step', 'text': 'together, with no obligation.'},
    ]


class ContactPageSettings(models.Model):
    """Everything editable on the Contact page (single row, managed in the dashboard)."""
    WORKING_DAYS = [
        ('mon_fri', 'Monday to Friday'),
        ('mon_sat', 'Monday to Saturday'),
        ('all', 'Every day'),
    ]

    # Hero
    page_subtitle = models.CharField(max_length=200, default='Tell us what you need. Our team replies within 1–2 business days.')

    # Form
    form_heading = models.CharField(max_length=60, default='Send us a')
    form_heading_highlight = models.CharField(max_length=40, default='message', help_text='Shown in the brand gradient after the heading.')
    message_placeholder = models.CharField('Message label', max_length=80, default='How can we help?')
    consent_text = models.CharField(max_length=250, default='I agree to TM Solutech contacting me about this enquiry, as described in the')
    submit_label = models.CharField(max_length=40, default='Send message')
    privacy_note = models.CharField(max_length=120, default='Your details are only used to reply to this enquiry.')
    default_country = models.CharField('Default phone country', max_length=2, default='IN', help_text='Two-letter country code, e.g. IN, US, GB, AE.')
    success_title = models.CharField(max_length=60, default='Message sent')
    success_message = models.CharField(max_length=250, default='Thank you! Your enquiry has reached our team. We reply within 1–2 business days.')

    # Reply card
    reply_title = models.CharField(max_length=60, default='We reply within')
    reply_time = models.CharField(max_length=40, default='1–2 business days', help_text='Shown in the brand gradient.')
    reply_text = models.CharField(max_length=200, blank=True, default='Every enquiry is read by our team and answered personally.')
    reply_steps = models.JSONField(default=default_reply_steps, blank=True)

    # Contact details
    show_details = models.BooleanField('Show contact details card', default=True)
    office_days = models.CharField(max_length=10, choices=WORKING_DAYS, default='mon_sat')
    office_open = models.TimeField(default=datetime.time(9, 30))
    office_close = models.TimeField(default=datetime.time(18, 30))
    show_open_status = models.BooleanField('Show live "Open now" badge', default=True)

    # Socials & map
    show_socials = models.BooleanField('Show social links card', default=True)
    socials_title = models.CharField(max_length=60, default='Follow TM Solutech')
    show_map = models.BooleanField('Show map section', default=True)
    map_heading = models.CharField(max_length=40, default='Our')
    map_heading_highlight = models.CharField(max_length=40, default='office')

    # Email
    notify_email = models.EmailField('Send enquiries to', blank=True, help_text='Leave empty to use the site default. One inbox.')
    send_acknowledgement = models.BooleanField('Email the visitor a confirmation', default=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contact Page'
        verbose_name_plural = 'Contact Page'

    def __str__(self):
        return 'Contact page settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def office_days_label(self):
        return {'mon_fri': 'Mon – Fri', 'mon_sat': 'Mon – Sat', 'all': 'Every day'}[self.office_days]

    @property
    def office_hours_label(self):
        fmt = lambda t: t.strftime('%I:%M %p').lstrip('0')
        return f'{self.office_days_label}, {fmt(self.office_open)} – {fmt(self.office_close)}'

    @property
    def open_weekdays(self):
        """ISO weekday numbers (Mon=1) the office is open, for the live badge."""
        return {'mon_fri': [1, 2, 3, 4, 5], 'mon_sat': [1, 2, 3, 4, 5, 6], 'all': [1, 2, 3, 4, 5, 6, 7]}[self.office_days]
