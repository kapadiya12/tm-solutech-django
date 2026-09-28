from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from .models import ContactInquiry


def contact_page(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            
            # Send notification email
            try:
                subject = f'New Contact Inquiry: {inquiry.subject or "General Inquiry"}'
                message = f"""New contact form submission:

Name: {inquiry.name}
Company: {inquiry.company}
Email: {inquiry.email}
Phone: {inquiry.phone or 'Not provided'}
Subject: {inquiry.subject or 'Not specified'}
Service: {inquiry.service or 'Not specified'}

Message:
{inquiry.message}

---
This is an automated notification from the TM Solutech website."""
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass
            
            messages.success(request, 'Thank you for your inquiry! We will get back to you within 24 hours.')
            return redirect('contact:contact')
    else:
        form = ContactForm()
    
    context = {
        'form': form,
        'page_title': 'Contact Us',
        'page_subtitle': 'Get in touch with our team for a free consultation',
    }
    return render(request, 'contact/contact.html', context)
