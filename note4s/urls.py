# -*- coding: utf-8 -*-

"""
    urls.py
    ~~~~~~~
"""
from note4s.handlers import LoginHandler, RegisterHandler, \
    NoteHandler, NotebookHandler

api_handlers = [
    (r'/auth/login/?', LoginHandler),
    (r'/auth/register/?', RegisterHandler),
    (r'/api/note/?', NoteHandler),
    (r'/api/notebook/?', NotebookHandler)
]

handlers = api_handlers
