from django.conf.urls import patterns, url
from lazyloader import views

urlpatterns = patterns('',

    url(r'^(?P<app_label>\w+)-(?P<model_name>\w+)-html-(?P<start>\d+)-(?P<end>\d+)/$', views.view_html, name='Html'),
    url(r'^(?P<app_label>\w+)-(?P<model_name>\w+)-json-(?P<start>\d+)-(?P<end>\d+)/$', views.view_json, name='Json'),
    url(r'^demo/$', views.demo, name='Demo')
)