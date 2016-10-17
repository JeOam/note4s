# -*- coding: utf-8 -*-

"""
    urls.py
    ~~~~~~~
"""
from note4s.handlers import LoginHandler, RegisterHandler, NoteHandler

api_handlers = [
    (r'/auth/login/?', LoginHandler),
    (r'/auth/register/?', RegisterHandler),
    (r'/api/note/?', NoteHandler)
]

handlers = api_handlers