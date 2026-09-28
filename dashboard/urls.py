from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
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
]
