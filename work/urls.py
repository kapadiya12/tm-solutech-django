from django.urls import path

from . import views

app_name = 'work'

urlpatterns = [
    path('', views.work_list, name='list'),
    path('<slug:slug>/', views.work_detail, name='detail'),
]
