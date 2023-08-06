#coding: utf-8
from django.conf.urls import patterns, url
from ma_settings.views import HomeView


urlpatterns = patterns('',
    url(r'^$',  HomeView.as_view(), name="master_settings_home"),
)