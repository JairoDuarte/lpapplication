from django.conf.urls import url

from . import views

app_name = 'lp'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'login/', views.login, name='login'),
    url(r'apply/', views.apply, name='apply'),
]
