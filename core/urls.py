from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about-us/', views.about, name='about'),
    path('why-us/', views.why_us, name='why_us'),
    path('leadership/', views.leadership_page, name='leadership'),
    path('clients/', views.clients_page, name='clients'),
    path('faqs/', views.faq_page, name='faqs'),
    path('search/', views.search, name='search'),
    path('search/suggest/', views.search_suggest, name='search_suggest'),
]
