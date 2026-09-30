from django import forms
from core.models import (
    SiteSettings, WhyUsReason, Testimonial, Leadership, FAQ, Statistic, Gallery, SEOSettings,
    Capability, ClientLogo, HeroTag, HeroStat, HeroSlide,
)
from services.models import ServiceCategory, Service, Industry
from insights.models import BlogPost, BlogCategory
from cms.models import Page


class FormStyleMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in ('icon', 'tab_icon') and isinstance(field.widget, forms.TextInput):
                field.widget.attrs.setdefault('data-icon-picker', '1')
                field.widget.attrs.setdefault('autocomplete', 'off')
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.URLInput, forms.NumberInput, forms.Select, forms.Textarea)):
                field.widget.attrs.setdefault('class', 'form-control')
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.setdefault('class', 'form-control')


class IconInput(forms.TextInput):
    """Text input enhanced into a visual icon picker by dashboard-editor.js."""
    def __init__(self, attrs=None):
        attrs = {'data-icon-picker': '1', 'placeholder': 'fas fa-cloud', 'autocomplete': 'off', **(attrs or {})}
        super().__init__(attrs)


import re as _re
from django.utils.html import strip_tags as _strip_tags

ICON_RE = _re.compile(r'^fa[srb]? fa-[a-z0-9-]+$')


class ItemsField(forms.JSONField):
    """Rows edited with the dashboard repeater. Every key is required and a minimum count applies."""
    def __init__(self, keys, min_items=1, max_items=12, noun='item', **kwargs):
        self.keys, self.min_items, self.max_items, self.noun = keys, min_items, max_items, noun
        kwargs.setdefault('required', False)
        kwargs.setdefault('widget', forms.HiddenInput(attrs={'data-items': '1'}))
        super().__init__(**kwargs)

    def clean(self, value):
        value = super().clean(value) or []
        if not isinstance(value, list):
            raise forms.ValidationError('Invalid data.')
        rows = []
        for row in value:
            if not isinstance(row, dict):
                continue
            row = {k: str(row.get(k, '')).strip()[:600] for k in self.keys}
            if not any(row.values()):
                continue  # fully empty row: ignore
            if not all(row.values()):
                raise forms.ValidationError(f'Every {self.noun} needs all its fields filled in.')
            if 'icon' in row and not ICON_RE.match(row['icon']):
                raise forms.ValidationError(f'One {self.noun} has an invalid icon. Use "Choose icon".')
            rows.append(row)
        if len(rows) < self.min_items:
            raise forms.ValidationError(f'Add at least {self.min_items} {self.noun}s.')
        if len(rows) > self.max_items:
            raise forms.ValidationError(f'Please keep this to {self.max_items} {self.noun}s or fewer.')
        return rows


def _unique_slug_error(model, slug, instance):
    qs = model.objects.filter(slug=slug)
    if instance and instance.pk:
        qs = qs.exclude(pk=instance.pk)
    return qs.exists()


def _text_len(html):
    return len(_strip_tags(html or '').replace('&nbsp;', ' ').strip())


class _ContentFormMixin:
    """Shared rules for services and categories. Rules are mirrored in the browser for live validation."""
    name_field = 'title'
    rules = {}

    def _apply_rules(self):
        for name, rule in self.rules.items():
            field = self.fields.get(name)
            if not field:
                continue
            field.required = rule.get('required', True)
            attrs = field.widget.attrs
            if field.required:
                attrs['data-required'] = '1'
            if 'min' in rule:
                attrs['data-minlen'] = rule['min']
            if 'max' in rule:
                attrs['data-maxchars'] = rule['max']
                attrs['maxlength'] = rule['max']
            if rule.get('richtext'):
                attrs['data-richtext'] = '1'
        self.fields['icon'].widget.attrs['data-required'] = '1'
        self.fields['slug'].widget.attrs['data-required'] = '1'
        if not (self.instance and self.instance.pk) and not self.is_bound:
            self.initial.setdefault('icon', '')  # make the admin choose an icon deliberately

    def _clean_len(self, name):
        value = (self.cleaned_data.get(name) or '').strip()
        rule = self.rules[name]
        n = _text_len(value) if rule.get('richtext') else len(value)
        if rule.get('min') and n < rule['min']:
            raise forms.ValidationError(f'Please write at least {rule["min"]} characters (currently {n}).')
        return value

    def clean_icon(self):
        icon = (self.cleaned_data.get('icon') or '').strip()
        if not ICON_RE.match(icon):
            raise forms.ValidationError('Please choose an icon with "Choose icon".')
        return icon

    def clean_short_description(self):
        return self._clean_len('short_description')

    def clean_description(self):
        return self._clean_len('description')

    def clean_slug(self):
        from django.utils.text import slugify
        slug = slugify(self.cleaned_data.get('slug') or self.data.get(self.name_field, ''))[:190]
        if not slug:
            raise forms.ValidationError('Enter a name first; the address is created from it.')
        if _unique_slug_error(self._meta.model, slug, self.instance):
            raise forms.ValidationError('Another page already uses this address. Please change the name or edit the address.')
        return slug


class ServiceCategoryForm(_ContentFormMixin, FormStyleMixin, forms.ModelForm):
    name_field = 'name'
    rules = {
        'name': {'min': 3, 'max': 80},
        'short_description': {'min': 40, 'max': 300},
        'description': {'min': 100, 'max': 3000},
    }

    class Meta:
        model = ServiceCategory
        fields = ['name', 'slug', 'icon', 'short_description', 'description', 'show_in_nav', 'is_active']
        labels = {
            'name': 'Category name',
            'slug': 'Page address',
            'short_description': 'Short summary',
            'description': 'Page introduction',
            'show_in_nav': 'Show in navbar',
            'is_active': 'Published',
        }
        help_texts = {
            'name': 'Shown in the navbar menu, on the homepage and as the page title. E.g. "Cloud Solutions".',
            'short_description': 'Shown under the category in the navbar menu, on homepage cards and in search.',
            'description': 'The introduction paragraph at the top of the category page.',
            'show_in_nav': 'Show this category as a column in the website\'s Services menu.',
            'is_active': 'When off, this category and all its services are hidden from the website.',
        }
        widgets = {
            'icon': IconInput(),
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 6}),
            'slug': forms.TextInput(attrs={'data-slug-from': 'id_name'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['slug'].help_text = 'Created automatically from the name.'
        self._apply_rules()

    def clean_name(self):
        return self._clean_len('name')


class ServiceForm(_ContentFormMixin, FormStyleMixin, forms.ModelForm):
    rules = {
        'title': {'min': 3, 'max': 120},
        'short_description': {'min': 40, 'max': 300},
        'description': {'min': 150, 'richtext': True},
    }
    feature_items = ItemsField(keys=['icon', 'title', 'text'], min_items=3, noun='feature', label='Key features')
    benefit_items = ItemsField(keys=['title', 'text'], min_items=2, noun='benefit', label='Benefits')
    process_items = ItemsField(keys=['title', 'text'], min_items=3, noun='step', label='Process steps')
    faq_items = ItemsField(keys=['question', 'answer'], min_items=2, max_items=20, noun='question', label='FAQs')

    class Meta:
        model = Service
        fields = [
            'category', 'title', 'slug', 'icon', 'short_description', 'image', 'description',
            'feature_items', 'benefit_items', 'process_items', 'faq_items',
            'show_in_nav', 'nav_badge', 'is_active',
        ]
        labels = {
            'title': 'Service name',
            'slug': 'Page address',
            'category': 'Service area',
            'short_description': 'Short summary',
            'description': 'Overview',
            'image': 'Overview image',
            'show_in_nav': 'Show in navbar',
            'nav_badge': 'Navbar badge',
            'is_active': 'Published',
        }
        help_texts = {
            'title': 'Shown as the page title, in the navbar menu and in search.',
            'category': 'Decides the page address and which navbar column the service appears in.',
            'short_description': 'Shown under the page title, in the navbar menu, on cards and in search.',
            'description': 'The main introduction on the service page. Use headings, lists and bold text.',
            'image': 'Shown beside the overview. JPG or PNG, landscape, at least 1200×800.',
            'show_in_nav': 'List this service in the website\'s Services menu.',
            'nav_badge': 'Optional highlight next to the name in the navbar menu.',
            'is_active': 'When off, the page is hidden from the website, the navbar and search.',
        }
        widgets = {
            'icon': IconInput(),
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'slug': forms.TextInput(attrs={'data-slug-from': 'id_title'}),
            'image': forms.FileInput(attrs={'accept': 'image/jpeg,image/png,image/webp', 'data-image-input': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['slug'].help_text = 'Created automatically from the name.'
        self.fields['category'].empty_label = 'Choose a service area…'
        self.fields['category'].widget.attrs['data-required'] = '1'
        self.fields['nav_badge'].choices = [('', 'No badge'), ('new', 'New'), ('popular', 'Popular')]
        self._apply_rules()
        image = self.fields['image']
        has_image = bool(self.instance and self.instance.pk and self.instance.image)
        image.required = not has_image
        image.widget.attrs['data-required'] = '1'
        image.show_required = True
        if has_image:
            image.widget.attrs['data-current'] = self.instance.image.url

    def clean_title(self):
        return self._clean_len('title')

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image and not (self.instance and self.instance.image):
            raise forms.ValidationError('Please upload an overview image.')
        if image and getattr(image, 'size', 0) > 5 * 1024 * 1024:
            raise forms.ValidationError('Image is larger than 5 MB. Please use a smaller file.')
        return image or self.instance.image


class IndustryForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Industry
        fields = '__all__'


class LeadershipForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Leadership
        fields = '__all__'


class BlogPostForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = BlogPost
        exclude = ['author']


class BlogCategoryForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = BlogCategory
        fields = '__all__'


class FAQForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = FAQ
        fields = '__all__'


class SiteSettingsForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = '__all__'


class PageForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Page
        fields = '__all__'


class StatisticForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Statistic
        fields = '__all__'


class TestimonialForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = '__all__'


class GalleryForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Gallery
        fields = '__all__'


class WhyUsReasonForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = WhyUsReason
        fields = '__all__'


class CapabilityForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Capability
        fields = '__all__'


class ClientLogoForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = ClientLogo
        fields = '__all__'


class HeroTagForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = HeroTag
        fields = '__all__'


class HeroStatForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = HeroStat
        fields = '__all__'


class HeroSlideForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = HeroSlide
        fields = '__all__'
