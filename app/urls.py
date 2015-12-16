# coding=utf-8

from django.conf.urls import url
from .views import index, create, profile, hello

__author__ = 'JeOam'

urlpatterns = [
    url(r'hello$', hello),
    url(r'create$', create),
    url(r'profile$', profile),
    url(r'^$', index),
]