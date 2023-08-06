# coding=utf-8

from django.conf.urls import patterns, include, url

from smsc import views as _views


urlpatterns = patterns('smsc.views',
    url(r'^callback/$', _views.CallbackView.as_view(), name='smsc_callback'),
)
