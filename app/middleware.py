# coding=utf-8

from django.shortcuts import redirect

__author__ = 'JeOam'

AUTH_URL = [
    "/admin/login/"
]

class AuthMiddleware(object):
    def process_request(self, request):
        """
        如果用户还未登录，切换到登录界面
        """
        if request.user.is_authenticated() is False and \
           request.path not in AUTH_URL:
            return redirect('/admin/login/')
