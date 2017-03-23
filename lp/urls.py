from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = 'lp'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'login/', auth_views.login, {'template_name': 'lp/login.html'}, name='login'),
    url(r'change-password/', views.password_change, name='password_change'),
    url(r'change-password/done/', auth_views.password_change_done, name='password_change_done'),
    url(r'reset-password/', auth_views.password_reset, {'template_name': 'lp/password_reset.html', 'email_template_name': 'lp/password_reset_email.html'}, name='password_reset'),
    url(r'set-password/', views.set_password, name='set_password'),
    url(r'logout/', views.logout, name='logout'),
    url(r'apply/', views.apply, name='apply'),
    url(r'confirm/', views.confirm, name='confirm'),
    url(r'confirm-email/', views.confirm_email, name='confirm_email'),
    url(r'candidat/', views.panel, name='panel'),
]
