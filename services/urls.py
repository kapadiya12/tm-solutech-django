from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('industries/', views.industry_list, name='industry_list'),
    path('industries/<slug:slug>/', views.industry_detail, name='industry_detail'),
    path('<slug:category_slug>/', views.category_detail, name='category_detail'),
    path('<slug:category_slug>/<slug:service_slug>/', views.service_detail, name='service_detail'),
]
