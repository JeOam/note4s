# coding=utf-8

from django.conf.urls import url
from .views import index, create, profile, hello, \
    index_edit_notebook

__author__ = 'JeOam'

urlpatterns = [
    url(r'hello$', hello),
    url(r'create$', create),
    url(r'profile$', profile),
    url(r'edit-notebook$', index_edit_notebook),
    url(r'^$', index),
]