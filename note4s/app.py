# -*- coding: utf-8 -*-

"""
    app.py
    ~~~~~~~
"""
import tornado
from note4s.urls import handlers
from note4s.handlers.base import BaseRequestHandler

def app(*args, **kwargs):
    return tornado.web.Application(
        handlers,
        default_handler_class=BaseRequestHandler,
        *args,
        **kwargs
    )
