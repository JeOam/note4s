# coding=utf-8

from django.shortcuts import render_to_response

__author__ = 'JeOam'


def note_detail(request, uuid_str):
    """
    返回笔记详情页
    """
    return render_to_response("app/note_detail.html")
