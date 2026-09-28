from django import forms
from core.models import SiteSettings, WhyUsReason, Testimonial, Leadership, FAQ, Statistic, Gallery, SEOSettings
from services.models import ServiceCategory, Service, Industry
from insights.models import BlogPost, BlogCategory
from cms.models import Page


class FormStyleMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.URLInput, forms.NumberInput, forms.Select, forms.Textarea)):
                field.widget.attrs.setdefault('class', 'form-control')
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.setdefault('class', 'form-control')


class ServiceCategoryForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = '__all__'


class ServiceForm(FormStyleMixin, forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'


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
