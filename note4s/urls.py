# -*- coding: utf-8 -*-

"""
    urls.py
    ~~~~~~~
"""
from note4s.handlers import LoginHandler, RegisterHandler, \
    CheckHandler, ProfileHandler, \
    NoteHandler, SubNoteHandler, \
    WatchNoteHandler, StarNoteHandler, \
    NotebookHandler

api_handlers = [
    (r'/auth/login/', LoginHandler),
    (r'/auth/register/?', RegisterHandler),
    (r'/auth/checkusername/', CheckHandler),
    (r'/api/profile/', ProfileHandler),
    (r'/api/note/', NoteHandler),
    (r'/api/subnote/', SubNoteHandler),
    (r'/api/note/(?P<note_id>[0-9a-f]{32}\Z)?', NoteHandler),
    (r'/api/note/watch/(?P<note_id>[0-9a-f]{32}\Z)?', WatchNoteHandler),
    (r'/api/note/star/(?P<note_id>[0-9a-f]{32}\Z)?', StarNoteHandler),
    (r'/api/notebook/?', NotebookHandler),
    (r'/api/notebook/(?P<notebook_id>[0-9a-f]{32}\Z)?', NotebookHandler)

]

handlers = api_handlers
