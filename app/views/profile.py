# coding=utf-8

from django.shortcuts import render_to_response

__author__ = 'JeOam'

def profile(request):
    return render_to_response("app/profile.html")
