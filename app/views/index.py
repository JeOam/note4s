# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse

__author__ = 'JeOam'


def hello(request):
    return HttpResponse("Hello, world.")

def index(request):
    return render(request, "app/index.html")