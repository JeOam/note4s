# -*- coding: utf-8 -*-

"""
    urls.py
    ~~~~~~~
"""
from note4s.handlers import LoginHandler, RegisterHandler, \
    CheckHandler, ProfileHandler, \
    NoteHandler, NoteDetailHandler, \
    NotebookHandler

api_handlers = [
    (r'/auth/login/?', LoginHandler),
    (r'/auth/register/?', RegisterHandler),
    (r'/auth/checkusername/', CheckHandler),
    (r'/api/profile/', ProfileHandler),
    (r'/api/note/', NoteHandler),
    (r'/api/note/(?P<note_id>[0-9a-f]{32}\Z)?', NoteDetailHandler),
    (r'/api/notebook/?', NotebookHandler)
]

handlers = api_handlers
