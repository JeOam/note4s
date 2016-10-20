# -*- coding: utf-8 -*-

"""
    app.py
    ~~~~~~~
"""
import tornado
from note4s.urls import handlers


def app(*args, **kwargs):
    return tornado.web.Application(handlers, *args, **kwargs)
