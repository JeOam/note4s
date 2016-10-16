# -*- coding: utf-8 -*-

"""
    urls.py
    ~~~~~~~
"""
from note4s.handlers import LoginHandler, RegisterHandler

api_handlers = [
    (r'/api/login/?', LoginHandler),
    (r'/api/register/?', RegisterHandler)
]

handlers = api_handlers