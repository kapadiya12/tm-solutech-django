from django.urls import path
from . import views

app_name = 'insights'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('search/', views.post_search, name='post_search'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
    path('<slug:slug>/helpful/', views.post_helpful, name='post_helpful'),
]
