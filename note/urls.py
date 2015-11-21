# coding=utf-8

from django.conf.urls import include, url
from .views import hello

__author__ = 'JeOam'


urlpatterns = [
    url(r'', hello)
]