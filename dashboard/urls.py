from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('run-migrations/', views.run_migrations, name='run_migrations'),
    # Navbar → Services Menu
    path('navbar/services/', views.navbar_services, name='navbar_services'),
    path('navbar/services/update/', views.navbar_services_update, name='navbar_services_update'),
    # Services
    path('services/', views.service_list, name='service_list'),
    path('services/create/', views.service_create, name='service_create'),
    path('services/<int:pk>/edit/', views.service_edit, name='service_edit'),
    path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    # Industries
    path('industries/', views.industry_list, name='industry_list'),
    path('industries/create/', views.industry_create, name='industry_create'),
    path('industries/<int:pk>/edit/', views.industry_edit, name='industry_edit'),
    path('industries/<int:pk>/delete/', views.industry_delete, name='industry_delete'),
    # Leadership
    path('leadership/', views.leadership_list, name='leadership_list'),
    path('leadership/create/', views.leadership_create, name='leadership_create'),
    path('leadership/<int:pk>/edit/', views.leadership_edit, name='leadership_edit'),
    path('leadership/<int:pk>/delete/', views.leadership_delete, name='leadership_delete'),
    # Blog
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/create/', views.blog_create, name='blog_create'),
    path('blog/<int:pk>/edit/', views.blog_edit, name='blog_edit'),
    path('blog/<int:pk>/delete/', views.blog_delete, name='blog_delete'),
    # FAQs
    path('faqs/', views.faq_list, name='faq_list'),
    path('faqs/create/', views.faq_create, name='faq_create'),
    path('faqs/<int:pk>/edit/', views.faq_edit, name='faq_edit'),
    path('faqs/<int:pk>/delete/', views.faq_delete, name='faq_delete'),
    # Inquiries
    path('inquiries/', views.inquiry_list, name='inquiry_list'),
    path('inquiries/<int:pk>/', views.inquiry_detail, name='inquiry_detail'),
    path('inquiries/<int:pk>/delete/', views.inquiry_delete, name='inquiry_delete'),
    # Settings
    path('settings/', views.site_settings_edit, name='site_settings'),
    # Pages
    path('pages/', views.page_list, name='page_list'),
    path('pages/create/', views.page_create, name='page_create'),
    path('pages/<int:pk>/edit/', views.page_edit, name='page_edit'),
    path('pages/<int:pk>/delete/', views.page_delete, name='page_delete'),
    # Statistics
    path('statistics/', views.statistic_list, name='statistic_list'),
    path('statistics/create/', views.statistic_create, name='statistic_create'),
    path('statistics/<int:pk>/edit/', views.statistic_edit, name='statistic_edit'),
    path('statistics/<int:pk>/delete/', views.statistic_delete, name='statistic_delete'),
    # Why Us Reasons
    path('why-us/', views.whyus_list, name='whyus_list'),
    path('why-us/create/', views.whyus_create, name='whyus_create'),
    path('why-us/<int:pk>/edit/', views.whyus_edit, name='whyus_edit'),
    path('why-us/<int:pk>/delete/', views.whyus_delete, name='whyus_delete'),
    # Blog Categories
    path('blog-categories/', views.blogcategory_list, name='blogcategory_list'),
    path('blog-categories/create/', views.blogcategory_create, name='blogcategory_create'),
    path('blog-categories/<int:pk>/edit/', views.blogcategory_edit, name='blogcategory_edit'),
    path('blog-categories/<int:pk>/delete/', views.blogcategory_delete, name='blogcategory_delete'),
    # Capabilities
    path('capabilities/', views.capability_list, name='capability_list'),
    path('capabilities/create/', views.capability_create, name='capability_create'),
    path('capabilities/<int:pk>/edit/', views.capability_edit, name='capability_edit'),
    path('capabilities/<int:pk>/delete/', views.capability_delete, name='capability_delete'),
    # Client Logos
    path('client-logos/', views.clientlogo_list, name='clientlogo_list'),
    path('client-logos/create/', views.clientlogo_create, name='clientlogo_create'),
    path('client-logos/<int:pk>/edit/', views.clientlogo_edit, name='clientlogo_edit'),
    path('client-logos/<int:pk>/delete/', views.clientlogo_delete, name='clientlogo_delete'),
    # Hero Tags
    path('hero-slides/', views.heroslide_list, name='heroslide_list'),
    path('hero-slides/create/', views.heroslide_create, name='heroslide_create'),
    path('hero-slides/<int:pk>/edit/', views.heroslide_edit, name='heroslide_edit'),
    path('hero-slides/<int:pk>/delete/', views.heroslide_delete, name='heroslide_delete'),
    path('hero-tags/', views.herotag_list, name='herotag_list'),
    path('hero-tags/create/', views.herotag_create, name='herotag_create'),
    path('hero-tags/<int:pk>/edit/', views.herotag_edit, name='herotag_edit'),
    path('hero-tags/<int:pk>/delete/', views.herotag_delete, name='herotag_delete'),
    # Hero Stats
    path('hero-stats/', views.herostat_list, name='herostat_list'),
    path('hero-stats/create/', views.herostat_create, name='herostat_create'),
    path('hero-stats/<int:pk>/edit/', views.herostat_edit, name='herostat_edit'),
    path('hero-stats/<int:pk>/delete/', views.herostat_delete, name='herostat_delete'),
]
