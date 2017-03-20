"""lpapplication URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from lp import views

urlpatterns = [
    url(r'^admin/settings/', views.admin_settings, name='admin_settings'),
    url(r'^admin/', admin.site.urls),
    url(r'change-password/done/', views.password_change_done, name='password_change_done'),
    url(r'reset-password/done/', views.password_reset_done, name='password_reset_done'),
    url(r'reset-password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.password_reset_confirm, name='password_reset_confirm'),
    url(r'reset-password/complete/', views.password_reset_complete, name='password_reset_complete'),
    url(r'', include('lp.urls')),
]
