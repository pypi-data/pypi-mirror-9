from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^$', views.newsletter),
    url(r'^unsubscribe/$', views.unsubscribe),
    url(r'^subscribe_default/$', views.subscribe_default),
    url(r'^subscribe_specific/$', views.subscribe_specific),
)
