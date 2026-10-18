from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    path('', views.contact_page, name='contact'),
    path('check-email/', views.check_email_view, name='check_email'),
]
