from django.conf.urls import patterns, url

from django.contrib.auth import views

urlpatterns = patterns('',
    url(r'^reset_password/$', views.password_reset, name='reset_password'),
    url(r'^reset_password/submitted/$', views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z]+)/(?P<token>.+)/$', views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/complete/$', views.password_reset_complete, name='password_reset_complete'),
)
