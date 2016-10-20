# -*- coding: utf-8 -*-

"""
    urls.py
    ~~~~~~~
"""
from note4s.handlers import LoginHandler, RegisterHandler, \
    NoteHandler, NoteDetailHandler, \
    NotebookHandler

api_handlers = [
    (r'/auth/login/?', LoginHandler),
    (r'/auth/register/?', RegisterHandler),
    (r'/api/note/', NoteHandler),
    (r'/api/note/(?P<note_id>[0-9a-f]{32}\Z)?', NoteDetailHandler),
    (r'/api/notebook/?', NotebookHandler)
]

handlers = api_handlers
