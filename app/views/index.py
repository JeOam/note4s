# coding=utf-8

from django.shortcuts import render_to_response
from django.http import HttpResponse

__author__ = 'JeOam'


def hello(request):
    return HttpResponse("Hello, world.")

def index(request):
    return render_to_response("app/index.html")
