# -*- coding: utf-8 -*-

"""
    urls.py
    ~~~~~~~
"""
from note4s.handlers import \
    LoginHandler, RegisterHandler, \
    FollowHandler, Unfollowandler, \
    CheckHandler, MentionHandler, ProfileHandler, \
    NoteHandler, SubNoteHandler, \
    WatchNoteHandler, StarNoteHandler, \
    NotebooksHandler, NotebookHandler, \
    NoteCommentHandler, StarCommentHandler, \
    NotificationHandler, ContributionHandler, \
    GithubCallbackHandler

api_handlers = [
    (r'/auth/github/', GithubCallbackHandler),
    (r'/auth/login/', LoginHandler),
    (r'/auth/register/?', RegisterHandler),
    (r'/auth/checkusername/', CheckHandler),
    (r'/api/profile/', ProfileHandler),
    (r'/api/user/mention/', MentionHandler),
    (r'/api/user/notification/', NotificationHandler),
    (r'/api/user/contribution/', ContributionHandler),
    (r'/api/user/follow/', FollowHandler),
    (r'/api/user/unfollow/', Unfollowandler),
    (r'/api/note/', NoteHandler),
    (r'/api/subnote/', SubNoteHandler),
    (r'/api/note/(?P<note_id>[0-9a-f]{32}\Z)?', NoteHandler),
    (r'/api/note/comment/(?P<note_id>[0-9a-f]{32}\Z)?', NoteCommentHandler),
    (r'/api/note/comment/star/(?P<comment_id>[0-9a-f]{32}\Z)?', StarCommentHandler),
    (r'/api/note/watch/(?P<note_id>[0-9a-f]{32}\Z)?', WatchNoteHandler),
    (r'/api/note/star/(?P<note_id>[0-9a-f]{32}\Z)?', StarNoteHandler),
    (r'/api/notebook/?', NotebooksHandler),
    (r'/api/notebook/(?P<notebook_id>[0-9a-f]{32}\Z)?', NotebookHandler)
]

handlers = api_handlers
