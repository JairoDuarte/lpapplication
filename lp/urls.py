from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = 'lp'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'login/', auth_views.login, {'template_name': 'lp/login.html'}, name='login'),
    url(r'logout/', views.logout, name='logout'),
    url(r'apply/', views.apply, name='apply'),
    url(r'confirm/', views.confirm, name='confirm'),
    url(r'confirm_email/', views.confirm_email, name='confirm_email'),
    url(r'candidat/', views.panel, name='panel'),
]
