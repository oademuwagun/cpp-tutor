from django.conf.urls import patterns, url

from visualcpp import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^execute/$', views.execute, name='execute'),
)