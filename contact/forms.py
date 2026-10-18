import re
import time

from django import forms
from django.core import signing

from services.models import ServiceCategory
from .models import ContactInquiry


TOPIC_CHOICES = [
    ('New project', 'New project'),
    ('Support', 'Support'),
    ('Partnership', 'Partnership'),
    ('Careers', 'Careers'),
    ('Other', 'Other'),
]

# Letters, with single separators or "dot + space" between parts (e.g. "Dr. R. K. Patel")
NAME_RE = re.compile(r"^[^\W\d_]+(?:(?:\. ?|[ '\-])[^\W\d_]+)*\.?$", re.UNICODE)
URL_RE = re.compile(r'(https?://|www\.)', re.IGNORECASE)

MESSAGE_MIN = 20
MESSAGE_MAX = 2000

# Spam timing: a human needs a few seconds; a stale form is re-issued
MIN_FILL_SECONDS = 3
MAX_FORM_AGE_SECONDS = 2 * 60 * 60
TOKEN_SALT = 'contact.form.issued'


def issue_form_token():
    """Signed timestamp embedded in the form so we can tell how fast it was filled."""
    return signing.dumps(int(time.time()), salt=TOKEN_SALT)


def service_choices():
    """Services grouped by area for the select (one query + prefetch)."""
    choices = [('', 'Select a service (optional)')]
    categories = (
        ServiceCategory.objects.filter(is_active=True)
        .prefetch_related('services')
        .order_by('display_order')
    )
    for category in categories:
        services = [s for s in category.services.all() if s.is_active]
        services.sort(key=lambda s: s.display_order)
        if services:
            choices.append((category.name, [(s.title, s.title) for s in services]))
    choices.append(('Other', [('Not sure yet', 'Not sure yet / need advice')]))
    return choices


class ContactForm(forms.ModelForm):
    topic = forms.ChoiceField(choices=TOPIC_CHOICES, initial='New project', widget=forms.RadioSelect)
    consent = forms.BooleanField(
        required=True,
        error_messages={'required': 'Please agree so we can contact you about your enquiry.'},
    )
    # Bot traps: a hidden field humans never fill, and a signed issue time
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'tabindex': '-1', 'autocomplete': 'off', 'class': 'cf-hp-input',
    }))
    form_token = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactInquiry
        fields = ['name', 'company', 'email', 'phone', 'service', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete': 'name', 'maxlength': 100}),
            'company': forms.TextInput(attrs={'autocomplete': 'organization', 'maxlength': 150}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email', 'maxlength': 254, 'inputmode': 'email'}),
            'phone': forms.TextInput(attrs={'autocomplete': 'tel', 'maxlength': 20, 'inputmode': 'tel'}),
            'message': forms.Textarea(attrs={'rows': 5, 'maxlength': MESSAGE_MAX}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'] = forms.ChoiceField(
            choices=service_choices(), required=False,
            widget=forms.Select(attrs={'class': 'cf-input', 'aria-describedby': 'err_service'}),
        )
        for name in ('name', 'company', 'email', 'message'):
            self.fields[name].required = True
        self.fields['phone'].required = False

        messages = {
            'name': 'Please enter your full name.',
            'company': 'Please enter your company name.',
            'email': 'Please enter your work email.',
            'message': 'Please tell us a little about what you need.',
        }
        for name, text in messages.items():
            self.fields[name].error_messages['required'] = text
        self.fields['email'].error_messages['invalid'] = 'Please enter a valid email address, like name@company.com.'

        if not self.is_bound:
            self.initial.setdefault('form_token', issue_form_token())

    # ---- field rules (mirrored client-side in static/js/contact.js) ----
    def clean_name(self):
        name = ' '.join(self.cleaned_data.get('name', '').split())
        if len(name) < 2:
            raise forms.ValidationError('Your name looks too short.')
        if len(name) > 100:
            raise forms.ValidationError('Please keep your name under 100 characters.')
        if not NAME_RE.match(name):
            raise forms.ValidationError("Use letters only. Spaces, dots, hyphens and apostrophes are fine.")
        return name

    def clean_company(self):
        company = ' '.join(self.cleaned_data.get('company', '').split())
        if len(company) < 2:
            raise forms.ValidationError('Your company name looks too short.')
        if len(company) > 150:
            raise forms.ValidationError('Please keep the company name under 150 characters.')
        if URL_RE.search(company):
            raise forms.ValidationError('Please enter the company name, not a link.')
        return company

    def clean_email(self):
        return self.cleaned_data.get('email', '').strip().lower()

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            return ''
        if not re.fullmatch(r'\+?[\d\s\-()]+', phone):
            raise forms.ValidationError('Use digits only. A leading + and spaces are fine.')
        digits = re.sub(r'\D', '', phone)
        if not 10 <= len(digits) <= 15:
            raise forms.ValidationError('Please enter a 10 to 15 digit phone number.')
        return phone

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if len(message) < MESSAGE_MIN:
            raise forms.ValidationError(f'Please add a little more detail (at least {MESSAGE_MIN} characters).')
        if len(message) > MESSAGE_MAX:
            raise forms.ValidationError(f'Please keep your message under {MESSAGE_MAX} characters.')
        if len(URL_RE.findall(message)) > 3:
            raise forms.ValidationError('Please remove some links. Messages with many links are blocked as spam.')
        return message

    def clean(self):
        cleaned = super().clean()
        self.is_spam = False
        if cleaned.get('website'):
            self.is_spam = True
        token = cleaned.get('form_token') or ''
        try:
            issued = int(signing.loads(token, salt=TOKEN_SALT))
        except (signing.BadSignature, TypeError, ValueError):
            self.is_spam = True
            return cleaned
        age = time.time() - issued
        if age < MIN_FILL_SECONDS:
            self.is_spam = True
        elif age > MAX_FORM_AGE_SECONDS:
            raise forms.ValidationError('This form was open for a long time. Please submit it again.')
        return cleaned

    def save(self, commit=True):
        inquiry = super().save(commit=False)
        inquiry.subject = self.cleaned_data.get('topic', '')
        if commit:
            inquiry.save()
        return inquiry
