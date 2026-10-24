from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field


class ServiceCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='services/categories/', blank=True)
    icon = models.CharField(max_length=50, default='fas fa-cogs')
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)

    # Navbar mega-menu
    show_in_nav = models.BooleanField('Show in navbar', default=True)
    nav_label = models.CharField('Navbar label', max_length=60, blank=True, help_text='Optional shorter name for the navbar. Defaults to the category name.')
    nav_description = models.CharField('Navbar description', max_length=160, blank=True, help_text='One line shown in the navbar. Defaults to the short description.')

    partners = models.ManyToManyField('core.Partner', blank=True, related_name='service_categories')

    class Meta:
        ordering = ['display_order']
        verbose_name = 'Service Category'
        verbose_name_plural = 'Service Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('services:category_detail', kwargs={'category_slug': self.slug})

    def active_services(self):
        return self.services.filter(is_active=True).order_by('display_order')

    @property
    def menu_label(self):
        return self.name

    @property
    def menu_description(self):
        return self.short_description


class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = CKEditor5Field('Description', config_name='extends', blank=True)
    image = models.ImageField(upload_to='services/', blank=True)
    icon = models.CharField(max_length=50, default='fas fa-server')
    features = CKEditor5Field('Features', config_name='extends', blank=True)
    benefits = CKEditor5Field('Benefits', config_name='extends', blank=True)
    process = CKEditor5Field('Process', config_name='extends', blank=True)
    faq = models.TextField(blank=True, help_text='Legacy JSON FAQs (superseded by faq_items).')

    # Structured page sections, edited as rows in the dashboard.
    # The legacy HTML fields above are kept only as a read fallback.
    feature_items = models.JSONField(default=list, blank=True, help_text='[{"icon", "title", "text"}]')
    benefit_items = models.JSONField(default=list, blank=True, help_text='[{"title", "text"}]')
    process_items = models.JSONField(default=list, blank=True, help_text='[{"title", "text"}]')
    faq_items = models.JSONField(default=list, blank=True, help_text='[{"question", "answer"}]')
    hero_stats = models.JSONField(default=list, blank=True, help_text='[{"value", "label"}]: optional key numbers in the page hero')
    partners = models.ManyToManyField('core.Partner', blank=True, related_name='services')
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    # Navbar mega-menu
    NAV_BADGE_CHOICES = [
        ('', 'None'),
        ('new', 'New'),
        ('popular', 'Popular'),
    ]
    show_in_nav = models.BooleanField('Show in navbar', default=True)
    nav_label = models.CharField('Navbar label', max_length=60, blank=True, help_text='Optional shorter name for the navbar. Defaults to the service title.')
    nav_description = models.CharField('Navbar description', max_length=160, blank=True, help_text='One line shown in the navbar. Defaults to the short description.')
    nav_badge = models.CharField('Navbar badge', max_length=10, choices=NAV_BADGE_CHOICES, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('services:service_detail', kwargs={
            'category_slug': self.category.slug,
            'service_slug': self.slug
        })

    @property
    def menu_label(self):
        return self.title

    @property
    def menu_description(self):
        return self.short_description

    @property
    def highlights(self):
        """Short chips for the hero: the first feature titles."""
        return [f.get('title') for f in (self.feature_items or [])[:3] if f.get('title')]

    def tech_partners(self):
        """Partners chosen for this service, else those of its category."""
        own = list(self.partners.filter(is_active=True))
        return own or list(self.category.partners.filter(is_active=True))

    def get_related_services(self):
        return Service.objects.filter(
            category=self.category, is_active=True
        ).exclude(pk=self.pk).select_related('category').order_by('display_order')[:8]


class Industry(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = CKEditor5Field('Description', config_name='extends', blank=True)
    image = models.ImageField(upload_to='industries/', blank=True)
    icon = models.CharField(max_length=50, default='fas fa-industry')
    benefits = CKEditor5Field('Benefits', config_name='extends', blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)

    class Meta:
        ordering = ['display_order']
        verbose_name_plural = 'Industries'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('services:industry_detail', kwargs={'slug': self.slug})


class ServicePageSettings(models.Model):
    """Single row: headings and calls to action shared by every service page."""
    features_badge = models.CharField(max_length=60, default="What's included")
    features_title = models.CharField(max_length=120, default='Key features')
    features_text = models.CharField(max_length=240, blank=True, default='Everything you get, delivered and supported by our certified engineers.')
    benefits_badge = models.CharField(max_length=60, default='Why it matters')
    benefits_title = models.CharField(max_length=120, default='Business benefits')
    benefits_text = models.CharField(max_length=240, blank=True, default='The outcomes our clients see when this is done right.')
    process_badge = models.CharField(max_length=60, default='How we work')
    process_title = models.CharField(max_length=120, default='Our delivery process')
    process_text = models.CharField(max_length=240, blank=True, default='A clear, proven path from first conversation to steady operation.')
    partners_badge = models.CharField(max_length=60, default='Technology partners')
    partners_title = models.CharField(max_length=120, default='Built on platforms you trust')
    partners_text = models.CharField(max_length=240, blank=True, default='We design, supply and support solutions from the world’s leading technology brands.')
    industries_badge = models.CharField(max_length=60, default='Industries')
    industries_title = models.CharField(max_length=120, default='Trusted across industries')
    industries_text = models.CharField(max_length=240, blank=True, default='Solutions shaped around the regulations and realities of your sector.')
    faq_badge = models.CharField(max_length=60, default='FAQ')
    faq_title = models.CharField(max_length=120, default='Frequently asked questions')
    related_badge = models.CharField(max_length=60, default='Explore more')
    related_title = models.CharField(max_length=120, default='Related services')
    cta_title = models.CharField(max_length=120, default='Ready to get started?')
    cta_text = models.CharField(max_length=240, blank=True, default='Talk to our team about your requirements. We usually reply within one business day.')
    cta_button = models.CharField(max_length=40, default='Get a free consultation')
    clients_title = models.CharField(max_length=120, default='Trusted by leading organisations')
    why_badge = models.CharField(max_length=60, default='Why TM Solutech')
    why_title = models.CharField(max_length=120, default='Why businesses choose us')
    why_text = models.CharField(max_length=240, blank=True, default='35+ years of heritage, one philosophy: your growth is our growth.')
    capabilities_badge = models.CharField(max_length=60, default='Capabilities')
    capabilities_title = models.CharField(max_length=120, default='Full-stack technology capabilities')
    capabilities_text = models.CharField(max_length=240, blank=True, default='One partner across the entire technology stack, from the network layer to the cloud, secured end to end.')
    testimonials_badge = models.CharField(max_length=60, default='Client stories')
    testimonials_title = models.CharField(max_length=120, default='What our clients say')
    show_stats = models.BooleanField('Show company stats band', default=True)
    show_clients = models.BooleanField('Show client logos', default=True)
    show_why_us = models.BooleanField('Show “Why TM Solutech”', default=True)
    show_capabilities = models.BooleanField('Show capabilities (Services page)', default=True)
    show_testimonials = models.BooleanField('Show client testimonials', default=True)
    show_partners = models.BooleanField('Show technology partners', default=True)
    show_industries = models.BooleanField('Show industries carousel', default=True)
    show_certifications = models.BooleanField('Show certifications', default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Service page settings'
        verbose_name_plural = 'Service page settings'

    def __str__(self):
        return 'Service page settings'

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
