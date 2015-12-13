# coding=utf-8

from django.conf.urls import url
from .views import index, create, profile

__author__ = 'JeOam'

urlpatterns = [
    url(r'create$', create),
    url(r'profile$', profile),
    url(r'^$', index),
]