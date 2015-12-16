# coding=utf-8

from django.http import HttpResponse

__author__ = 'JeOam'

def hello(request):
    return HttpResponse("hello world.")