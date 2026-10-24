from django import forms
from core.models import (
    SiteSettings, WhyUsReason, Testimonial, Leadership, FAQ, FAQCategory, Statistic, Gallery, SEOSettings,
    Capability, ClientLogo, HeroTag, HeroStat, HeroSlide, SocialLink, Partner, Certification,
)
from contact.models import ContactPageSettings
from services.models import ServiceCategory, Service, Industry, ServicePageSettings
from insights.models import BlogPost, BlogCategory
from work.models import CaseStudy
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
        fields = ['name', 'slug', 'icon', 'short_description', 'description', 'image', 'partners',
                  'meta_title', 'meta_description', 'show_in_nav', 'is_active']
        labels = {
            'image': 'Hero image',
            'partners': 'Technology partners',
            'meta_title': 'Google title',
            'meta_description': 'Google description',
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
            'image': 'Background of the category page hero and its banner on the Services page. Landscape, at least 1600×1000.',
            'partners': 'Brands shown on this category page and used by its services unless a service picks its own.',
            'show_in_nav': 'Show this category as a column in the website\'s Services menu.',
            'is_active': 'When off, this category and all its services are hidden from the website.',
        }
        widgets = {
            'icon': IconInput(),
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 6}),
            'slug': forms.TextInput(attrs={'data-slug-from': 'id_name'}),
            'image': forms.FileInput(attrs={'accept': 'image/jpeg,image/png,image/webp', 'data-image-input': '1'}),
            'partners': forms.CheckboxSelectMultiple,
            'meta_title': forms.TextInput(attrs={'maxlength': 70, 'data-count': '60'}),
            'meta_description': forms.Textarea(attrs={'rows': 2, 'maxlength': 200, 'data-count': '158'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['partners'].queryset = Partner.objects.filter(is_active=True)
        if self.instance.pk and self.instance.image:
            self.fields['image'].widget.attrs['data-current'] = self.instance.image.url
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
    hero_stats = ItemsField(keys=['value', 'label'], min_items=0, max_items=4, noun='number', label='Hero numbers')

    class Meta:
        model = Service
        fields = [
            'category', 'title', 'slug', 'icon', 'short_description', 'image', 'description',
            'feature_items', 'benefit_items', 'process_items', 'faq_items', 'hero_stats', 'partners',
            'meta_title', 'meta_description', 'show_in_nav', 'nav_badge', 'is_active',
        ]
        labels = {
            'title': 'Service name',
            'slug': 'Page address',
            'category': 'Service area',
            'short_description': 'Short summary',
            'description': 'Overview',
            'image': 'Hero image',
            'partners': 'Technology partners',
            'meta_title': 'Google title',
            'meta_description': 'Google description',
            'show_in_nav': 'Show in navbar',
            'nav_badge': 'Navbar badge',
            'is_active': 'Published',
        }
        help_texts = {
            'title': 'Shown as the page title, in the navbar menu and in search.',
            'category': 'Decides the page address and which navbar column the service appears in.',
            'short_description': 'Shown under the page title, in the navbar menu, on cards and in search.',
            'description': 'The main introduction on the service page. Use headings, lists and bold text.',
            'image': 'The large photo in the page hero, also used on cards and carousels. Landscape, at least 1400×900.',
            'partners': 'Brands shown in the partner logo strip on this page. Leave empty to use the service area\'s partners.',
            'meta_title': 'Title in Google results. Defaults to the service name.',
            'meta_description': 'Description in Google results. Defaults to the short summary.',
            'show_in_nav': 'List this service in the website\'s Services menu.',
            'nav_badge': 'Optional highlight next to the name in the navbar menu.',
            'is_active': 'When off, the page is hidden from the website, the navbar and search.',
        }
        widgets = {
            'icon': IconInput(),
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'slug': forms.TextInput(attrs={'data-slug-from': 'id_title'}),
            'image': forms.FileInput(attrs={'accept': 'image/jpeg,image/png,image/webp', 'data-image-input': '1'}),
            'partners': forms.CheckboxSelectMultiple,
            'meta_title': forms.TextInput(attrs={'maxlength': 70, 'data-count': '60'}),
            'meta_description': forms.Textarea(attrs={'rows': 2, 'maxlength': 200, 'data-count': '158'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['partners'].queryset = Partner.objects.filter(is_active=True)
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
        fields = ['title', 'slug', 'category', 'excerpt', 'featured_image', 'content', 'focus_keyword', 'tags',
                  'is_published', 'published_at', 'is_featured', 'meta_title', 'meta_description']
        widgets = {
            'published_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'excerpt': forms.Textarea(attrs={'rows': 3, 'maxlength': 300, 'data-count': '300'}),
            'meta_title': forms.TextInput(attrs={'maxlength': 70, 'data-count': '60'}),
            'meta_description': forms.Textarea(attrs={'rows': 2, 'maxlength': 200, 'data-count': '158'}),
            'tags': forms.TextInput(attrs={'placeholder': 'Cloud, Security, Compliance'}),
            'focus_keyword': forms.TextInput(attrs={'placeholder': 'e.g. CSCRF compliance', 'maxlength': 80}),
            'slug': forms.TextInput(attrs={'data-slug-from': 'id_title'}),
        }
        labels = {
            'is_published': 'Published',
            'published_at': 'Publish date & time',
            'is_featured': 'Feature on the Insights page',
            'excerpt': 'Summary',
            'slug': 'Web address',
        }
        help_texts = {
            'slug': 'The link to this article. Created from the title automatically; click Edit to customise it.',
            'excerpt': 'One or two sentences shown on cards and under the title.',
            'published_at': 'Leave empty to publish now. A future date schedules the post.',
            'tags': 'Comma separated. Visitors can click a tag to see related articles.',
            'meta_title': 'Title in Google results. Defaults to the post title.',
            'meta_description': 'Description in Google results and link previews. About 150 characters.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['published_at'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']
        self.fields['category'].empty_label = 'Choose a category'
        self.fields['slug'].required = False   # filled from the title when left empty
        for name in self.REQUIRED:
            self.fields[name].required = True
            self.fields[name].error_messages['required'] = {
                'title': 'Please enter a title.', 'category': 'Please choose a category.',
                'excerpt': 'Please write a short summary.', 'focus_keyword': 'Please add a focus keyword.',
                'tags': 'Add at least 2 tags, separated by commas.', 'meta_description': 'Please write a search description.',
            }[name]
        self.fields['content'].required = False   # checked in clean_content (CKEditor hides the textarea)
        self.fields['content'].show_required = True
        self.fields['featured_image'].required = False   # checked in clean_featured_image (keeps the current image on edit)
        self.fields['featured_image'].show_required = True
        self.fields['focus_keyword'].help_text = 'The main phrase people would search for. Used for the SEO score.'
        self.fields['tags'].help_text = 'At least 2, comma separated. Visitors can click a tag to see related articles.'
        self.fields['meta_description'].help_text = 'Shown in Google results and link previews. Write 120 to 160 characters.'

    REQUIRED = ('title', 'category', 'excerpt', 'focus_keyword', 'tags', 'meta_description')
    MIN_WORDS = 300

    def clean_title(self):
        title = ' '.join((self.cleaned_data.get('title') or '').split())
        if len(title) < 20:
            raise forms.ValidationError(f'Please write a fuller title: at least 20 characters (currently {len(title)}).')
        return title

    def clean_excerpt(self):
        text = ' '.join((self.cleaned_data.get('excerpt') or '').split())
        if len(text) < 60:
            raise forms.ValidationError(f'Write one or two full sentences: at least 60 characters (currently {len(text)}).')
        return text

    def clean_content(self):
        html = self.cleaned_data.get('content') or ''
        words = len(_strip_tags(html).replace('&nbsp;', ' ').split())
        if not words:
            raise forms.ValidationError('Please write the article.')
        if words < self.MIN_WORDS:
            raise forms.ValidationError(f'Articles need at least {self.MIN_WORDS} words (currently {words}).')
        return html

    def clean_featured_image(self):
        image = self.cleaned_data.get('featured_image')
        if image is False or not (image or (self.instance.pk and self.instance.featured_image)):
            raise forms.ValidationError('Please add a cover image. It is shown on cards, the article and link previews.')
        return image

    def clean_meta_description(self):
        text = ' '.join((self.cleaned_data.get('meta_description') or '').split())
        if len(text) < 70:
            raise forms.ValidationError(f'Too short for Google: write at least 70 characters, ideally 120 to 160 (currently {len(text)}).')
        return text

    def clean_slug(self):
        from django.utils.text import slugify
        slug = slugify(self.cleaned_data.get('slug') or self.data.get('title', ''))[:190]
        if not slug:
            raise forms.ValidationError('Enter a title first; the address is created from it.')
        if _unique_slug_error(BlogPost, slug, self.instance):
            raise forms.ValidationError('Another post already uses this address.')
        return slug

    def clean_tags(self):
        seen, tags = set(), []
        for t in (self.cleaned_data.get('tags') or '').split(','):
            t = ' '.join(t.split())
            if t and t.lower() not in seen:
                seen.add(t.lower()); tags.append(t)
        if len(tags) < 2:
            raise forms.ValidationError('Add at least 2 tags, separated by commas.')
        return ', '.join(tags)[:250]


class BlogCategoryForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = BlogCategory
        fields = ['name', 'slug', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Cybersecurity', 'maxlength': 60}),
            'slug': forms.TextInput(attrs={'data-slug-from': 'id_name'}),
            'description': forms.Textarea(attrs={'rows': 3, 'maxlength': 240, 'data-count': '200',
                                                 'placeholder': 'e.g. Guides on protecting your business from cyber threats, audits and compliance.'}),
        }
        labels = {
            'name': 'Category name',
            'slug': 'Web address',
            'description': 'Short intro',
            'is_active': 'Show on the website',
        }
        help_texts = {
            'name': 'Shown as a filter chip on the Insights page and as a label on each article.',
            'slug': 'The link to this topic. Created from the name automatically; only letters, numbers and dashes.',
            'description': 'Optional. Shown under the heading when a visitor picks this topic on the Insights page.',
            'is_active': 'When off, the topic chip is hidden. Its articles stay live and can still be found by search.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False   # filled from the name when left empty

    def clean_name(self):
        name = ' '.join((self.cleaned_data.get('name') or '').split())
        qs = BlogCategory.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('A category with this name already exists.')
        return name

    def clean_slug(self):
        from django.utils.text import slugify
        slug = slugify(self.cleaned_data.get('slug') or self.data.get('name', ''))[:190]
        if not slug:
            raise forms.ValidationError('Enter a name first; the address is created from it.')
        if _unique_slug_error(BlogCategory, slug, self.instance):
            raise forms.ValidationError('Another category already uses this address.')
        return slug

    def clean_description(self):
        return ' '.join((self.cleaned_data.get('description') or '').split())


class FAQForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'category', 'answer', 'is_active', 'is_popular', 'display_order']
        widgets = {
            'question': forms.TextInput(attrs={'placeholder': 'e.g. How is pricing structured?', 'maxlength': 200, 'data-count': '120'}),
        }
        labels = {
            'category': 'Topic',
            'is_active': 'Show on website',
            'is_popular': 'Popular question',
            'display_order': 'Order within topic',
        }
        help_texts = {
            'question': 'Write it the way a customer would ask it. End with a question mark.',
            'category': 'Questions are grouped by topic on the FAQs page.',
            'answer': 'Keep it short and direct: answer in the first sentence, then add detail. Link to a service or article where useful.',
            'is_active': 'When off, the question is only visible here.',
            'is_popular': 'Shown as a quick link at the top of the FAQs page, with a “Popular” badge.',
            'display_order': 'Lower numbers show first. You can also drag questions on the FAQs list.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.models import FAQCategory
        self.fields['category'].queryset = FAQCategory.objects.all()
        self.fields['category'].required = True
        self.fields['category'].empty_label = 'Choose a topic'
        self.fields['category'].error_messages['required'] = 'Please choose a topic.'
        self.fields['question'].error_messages['required'] = 'Please write the question.'
        self.fields['answer'].required = False
        self.fields['answer'].show_required = True

    def clean_question(self):
        q = ' '.join((self.cleaned_data.get('question') or '').split())
        if len(q) < 10:
            raise forms.ValidationError('Please write the full question (at least 10 characters).')
        if not q.endswith('?'):
            q += '?'
        dupes = FAQ.objects.filter(question__iexact=q)
        if self.instance.pk:
            dupes = dupes.exclude(pk=self.instance.pk)
        if dupes.exists():
            raise forms.ValidationError('This question already exists.')
        return q

    def clean_answer(self):
        html = self.cleaned_data.get('answer') or ''
        n = len(_strip_tags(html).replace('&nbsp;', ' ').strip())
        if n < 30:
            raise forms.ValidationError('Please write an answer of at least 30 characters.' if n else 'Please write the answer.')
        return html


class FAQCategoryForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = FAQCategory
        fields = ['name', 'slug', 'icon', 'description', 'display_order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Support & AMC', 'maxlength': 60}),
            'slug': forms.TextInput(attrs={'data-slug-from': 'id_name'}),
            'description': forms.TextInput(attrs={'placeholder': 'e.g. Support hours, maintenance contracts and raising requests.', 'maxlength': 140}),
        }
        labels = {
            'name': 'Topic name', 'slug': 'Web address', 'icon': 'Icon',
            'description': 'Short description', 'display_order': 'Display order', 'is_active': 'Show on website',
        }
        help_texts = {
            'name': 'Shown as the group heading and in the topics menu on the FAQs page.',
            'slug': 'Used for the link to this topic, e.g. /faqs/#topic-support. Created from the name.',
            'description': 'Optional. One line under the topic heading.',
            'display_order': 'Lower numbers show first.',
            'is_active': 'When off, the whole topic and its questions are hidden on the website.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False

    def clean_slug(self):
        from django.utils.text import slugify
        slug = slugify(self.cleaned_data.get('slug') or self.data.get('name', ''))[:80]
        if not slug:
            raise forms.ValidationError('Enter a name first; the address is created from it.')
        if _unique_slug_error(FAQCategory, slug, self.instance):
            raise forms.ValidationError('Another topic already uses this address.')
        return slug


class SiteSettingsForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = SiteSettings
        # Social profiles are managed in Dashboard → Social Links
        exclude = ['linkedin_url', 'instagram_url', 'facebook_url', 'youtube_url', 'whatsapp_number']


class SocialLinkForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = SocialLink
        fields = ['platform', 'url', 'label', 'icon', 'show_in_footer', 'show_on_contact', 'is_active', 'display_order']
        widgets = {'icon': IconInput()}

    def clean(self):
        cleaned = super().clean()
        platform = cleaned.get('platform')
        icon = (cleaned.get('icon') or '').strip()
        if platform == 'other' and not icon:
            self.add_error('icon', 'Choose an icon for a custom link.')
        if icon and not ICON_RE.match(icon):
            self.add_error('icon', 'Use "Choose icon" to pick a valid icon.')
        url = cleaned.get('url') or ''
        if platform == 'whatsapp' and url and 'wa.me/' not in url and 'whatsapp.com' not in url:
            self.add_error('url', 'For WhatsApp use a link like https://wa.me/917947717070.')
        return cleaned


class ContactPageSettingsForm(FormStyleMixin, forms.ModelForm):
    reply_steps = ItemsField(keys=['title', 'text'], min_items=0, max_items=5, noun='step')
    default_country = forms.ChoiceField(label='Default phone country')

    class Meta:
        model = ContactPageSettings
        exclude = ['updated_at']
        widgets = {
            'office_open': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'office_close': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from contact.phone import countries
        try:
            from babel import Locale  # optional, not required
            names = Locale('en').territories
        except Exception:
            names = {}
        self.fields['default_country'].choices = [
            (c['iso'], f"{names.get(c['iso'], c['iso'])} (+{c['dial']})") for c in countries()
        ]
        self.fields['default_country'].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned = super().clean()
        o, c = cleaned.get('office_open'), cleaned.get('office_close')
        if o and c and o >= c:
            self.add_error('office_close', 'Closing time must be after opening time.')
        return cleaned


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
        fields = ['name', 'logo', 'display_order', 'is_active']
        widgets = {'name': forms.TextInput(attrs={'placeholder': 'e.g. CEPT University', 'maxlength': 120})}
        labels = {'name': 'Client name', 'logo': 'Logo', 'display_order': 'Display order', 'is_active': 'Show on website'}
        help_texts = {
            'name': 'Used as the logo\'s alt text and shown on hover. Only add clients who agreed to be listed.',
            'logo': 'PNG with a transparent background works best, at least 300px wide.',
            'display_order': 'Lower numbers show first in the logo strip and on the Clients page.',
            'is_active': 'When off, the logo is hidden from the website.',
        }

    def clean_name(self):
        name = ' '.join((self.cleaned_data.get('name') or '').split())
        dupes = ClientLogo.objects.filter(name__iexact=name)
        if self.instance.pk:
            dupes = dupes.exclude(pk=self.instance.pk)
        if dupes.exists():
            raise forms.ValidationError('A client with this name already exists.')
        return name


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


class CaseStudyForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = CaseStudy
        fields = ['title', 'slug', 'summary', 'client_name', 'client_logo', 'industry', 'service', 'year',
                  'cover_image', 'challenge', 'solution', 'results', 'metrics',
                  'testimonial_quote', 'testimonial_author', 'is_published', 'is_featured', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. 24/7 managed SOC for a SEBI-regulated broker', 'maxlength': 160}),
            'slug': forms.TextInput(attrs={'data-slug-from': 'id_title'}),
            'summary': forms.Textarea(attrs={'rows': 2, 'maxlength': 300, 'data-count': '200'}),
            'client_name': forms.TextInput(attrs={'placeholder': 'e.g. ABC Securities, or leave empty'}),
            'year': forms.NumberInput(attrs={'placeholder': 'e.g. 2025', 'min': 1985, 'max': 2100}),
            'challenge': forms.Textarea(attrs={'rows': 5, 'placeholder': 'What problem did the client have? What was at stake?'}),
            'solution': forms.Textarea(attrs={'rows': 6, 'placeholder': 'What did TM Solutech deliver, and how?'}),
            'results': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Passed the SEBI CSCRF audit with zero findings\nAll branches monitored from one dashboard'}),
            'metrics': forms.Textarea(attrs={'rows': 3, 'placeholder': '40% | Less downtime\n24/7 | Threat monitoring\n3 weeks | To go live'}),
            'testimonial_quote': forms.Textarea(attrs={'rows': 3}),
            'testimonial_author': forms.TextInput(attrs={'placeholder': 'e.g. Rahul Mehta, CTO, ABC Securities'}),
        }
        labels = {
            'slug': 'Web address',
            'summary': 'Short summary',
            'client_name': 'Client name',
            'challenge': 'The challenge',
            'solution': 'What we delivered',
            'results': 'Results',
            'metrics': 'Key numbers',
            'testimonial_quote': 'Client quote',
            'testimonial_author': 'Quote by',
            'is_published': 'Published',
            'is_featured': 'Featured project',
            'order': 'Display order',
        }
        help_texts = {
            'slug': 'The link to this project. Created from the title automatically.',
            'summary': 'One or two sentences shown on the project card.',
            'client_name': 'Leave empty if the client can’t be named: it shows as “Confidential client”.',
            'client_logo': 'Only with the client’s permission. PNG with a transparent background works best.',
            'industry': 'Visitors can filter projects by industry.',
            'service': 'Links the case study to the service page.',
            'cover_image': 'Landscape, about 1600×900. Screenshots, photos of the setup or a diagram.',
            'challenge': 'Leave a blank line between paragraphs.',
            'solution': 'Leave a blank line between paragraphs.',
            'results': 'One result per line. Shown as a ticked list.',
            'metrics': 'Up to 4, one per line, as number | label. Shown as big highlighted numbers.',
            'is_published': 'When off, the project is only visible here.',
            'is_featured': 'Shown large at the top of the Our Work page.',
            'order': 'Lower numbers show first.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['industry'].empty_label = 'No industry'
        self.fields['service'].empty_label = 'No service'
        self.fields['results'].help_text += ' Add results or key numbers before publishing.'

    def clean_slug(self):
        from django.utils.text import slugify
        slug = slugify(self.cleaned_data.get('slug') or self.data.get('title', ''))[:170]
        if not slug:
            raise forms.ValidationError('Enter a title first; the address is created from it.')
        if _unique_slug_error(CaseStudy, slug, self.instance):
            raise forms.ValidationError('Another project already uses this address.')
        return slug

    def clean_metrics(self):
        lines = [l.strip() for l in (self.cleaned_data.get('metrics') or '').splitlines() if l.strip()]
        bad = [l for l in lines if '|' not in l or not all(p.strip() for p in l.split('|', 1))]
        if bad:
            raise forms.ValidationError(f'Use the format number | label, e.g. “40% | Less downtime”. Check: {bad[0]}')
        if len(lines) > 4:
            raise forms.ValidationError('Please keep this to 4 numbers or fewer.')
        return '\n'.join(lines)

    def clean(self):
        data = super().clean()
        if data.get('is_published') and not (data.get('results') or data.get('metrics')):
            self.add_error('results', 'Add at least one result or key number before publishing.')
        if data.get('testimonial_quote') and not data.get('testimonial_author'):
            self.add_error('testimonial_author', 'Say who the quote is from.')
        return data


class PartnerForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Partner
        fields = ['name', 'logo', 'category', 'website', 'display_order', 'is_active']
        labels = {'name': 'Brand name', 'display_order': 'Display order', 'is_active': 'Show on website'}
        help_texts = {
            'logo': 'SVG or PNG with a transparent background. Shown in the logo strips on service pages.',
            'category': 'Used to group partners.',
            'website': 'Optional.',
            'display_order': 'Lower numbers show first.',
            'is_active': 'When off, the logo is hidden everywhere.',
        }
        widgets = {'logo': forms.FileInput(attrs={'accept': 'image/svg+xml,image/png,image/webp,image/jpeg'})}

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo and hasattr(logo, 'name') and not logo.name.lower().endswith(('.svg', '.png', '.webp', '.jpg', '.jpeg')):
            raise forms.ValidationError('Please upload an SVG, PNG, WebP or JPG file.')
        if logo and getattr(logo, 'size', 0) > 2 * 1024 * 1024:
            raise forms.ValidationError('Logo is larger than 2 MB.')
        return logo


class CertificationForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['name', 'title', 'description', 'icon', 'logo', 'display_order', 'is_active']
        labels = {'name': 'Certification', 'title': 'Full name', 'logo': 'Badge image', 'display_order': 'Display order', 'is_active': 'Show on website'}
        help_texts = {
            'name': 'Short name, e.g. ISO 9001.',
            'title': 'e.g. Quality Management System.',
            'description': 'One line about what it means for clients.',
            'logo': 'Optional certificate badge. If empty, the icon is shown.',
            'is_active': 'When off, it is hidden from service pages.',
        }
        widgets = {'icon': IconInput(), 'description': forms.Textarea(attrs={'rows': 2, 'maxlength': 240})}


class ServicePageSettingsForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = ServicePageSettings
        exclude = ['updated_at']
        widgets = {f: forms.TextInput(attrs={'maxlength': 240}) for f in (
            'features_text', 'benefits_text', 'process_text', 'partners_text', 'industries_text', 'cta_text', 'why_text', 'capabilities_text')}

for _name in ServicePageSettingsForm.base_fields:
    _f = ServicePageSettingsForm.base_fields[_name]
    if _name.endswith('_badge'):
        _f.label = 'Badge'
    elif _name.endswith('_title'):
        _f.label = 'Heading'
    elif _name.endswith('_text'):
        _f.label = 'Intro line'
ServicePageSettingsForm.base_fields['cta_title'].label = 'Heading'
ServicePageSettingsForm.base_fields['clients_title'].label = 'Client logos heading'
ServicePageSettingsForm.base_fields['cta_button'].label = 'Button text'


class AssistantSettingsForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        from assistant.models import AssistantSettings
        model = AssistantSettings
        exclude = ['updated_at']
        widgets = {
            'greeting': forms.Textarea(attrs={'rows': 3}),
            'quick_replies': forms.Textarea(attrs={'rows': 4}),
            'personality': forms.Textarea(attrs={'rows': 3}),
            'extra_knowledge': forms.Textarea(attrs={'rows': 8, 'placeholder': 'e.g. Office hours are Mon–Sat, 10am–7pm.\nWe do not offer website design services.'}),
            'gemini_key': forms.PasswordInput(render_value=False, attrs={'autocomplete': 'new-password', 'placeholder': 'Leave empty to keep the current key'}),
            'temperature': forms.NumberInput(attrs={'step': '0.05', 'min': '0', 'max': '1'}),
        }
        help_texts = {
            'quick_replies': 'One per line (up to 6), shown as buttons when the chat opens.',
            'personality': 'How the assistant sounds. Facts come from the website automatically.',
            'max_messages': 'After this many messages in one chat, visitors are pointed to the team.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_key = self.instance.gemini_key

    def clean_gemini_key(self):
        return (self.cleaned_data.get('gemini_key') or '').strip() or self._old_key

    def clean_temperature(self):
        t = self.cleaned_data.get('temperature')
        if t is not None and not (0 <= t <= 1):
            raise forms.ValidationError('Use a value between 0 and 1.')
        return t


class TrainedAnswerForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        from assistant.models import TrainedAnswer
        model = TrainedAnswer
        fields = ['question', 'answer', 'is_active']
        widgets = {'answer': forms.Textarea(attrs={'rows': 5})}
        help_texts = {
            'question': 'Write it the way a visitor would ask. Similar questions get the same answer.',
            'answer': 'The exact, correct answer. Keep it short and factual; links like /contact/ work.',
        }
