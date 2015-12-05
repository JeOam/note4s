# coding=utf-8

from django.shortcuts import render

__author__ = 'JeOam'

def create(request):
    return render(request, "app/create.html")