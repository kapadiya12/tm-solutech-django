from django import forms
from .models import ContactInquiry
from services.models import ServiceCategory
import re


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ['name', 'company', 'email', 'phone', 'subject', 'service', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name',
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Company Name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91 XXXXXXXXXX',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject of your inquiry',
            }),
            'service': forms.Select(attrs={
                'class': 'form-control',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us about your requirements...',
                'rows': 5,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make service a dropdown from categories
        categories = ServiceCategory.objects.filter(is_active=True)
        choices = [('', 'Select a Service')] + [(c.name, c.name) for c in categories]
        self.fields['service'] = forms.ChoiceField(
            choices=choices,
            required=False,
            widget=forms.Select(attrs={'class': 'form-control'})
        )
        self.fields['name'].required = True
        self.fields['company'].required = True
        self.fields['email'].required = True
        self.fields['message'].required = True

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone:
            cleaned = re.sub(r'[\s\-\(\)]', '', phone)
            if not re.match(r'^\+?\d{7,15}$', cleaned):
                raise forms.ValidationError('Please enter a valid phone number.')
        return phone

    def clean_message(self):
        message = self.cleaned_data.get('message', '')
        if len(message) < 10:
            raise forms.ValidationError('Please provide more details (at least 10 characters).')
        return message
