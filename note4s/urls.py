# -*- coding: utf-8 -*-

"""
    urls.py
    ~~~~~~~
"""
from note4s.handlers import (
    comment,
    github,
    note,
    notebook,
    organization,
    user,
    upload
)

api_handlers = [
    (r'/auth/github/', github.GithubCallbackHandler),
    (r'/auth/login/', user.LoginHandler),
    (r'/auth/register/?', user.RegisterHandler),
    (r'/auth/checkusername/', user.CheckHandler),
    (r'/api/profile/', user.ProfileHandler),
    (r'/api/profile/(?P<user_id>[0-9a-f]{32}\Z)?', user.ProfileHandler),
    (r'/api/user/mention/', user.MentionHandler),
    (r'/api/user/notification/', user.NotificationHandler),
    (r'/api/user/contribution/', user.ContributionHandler),
    (r'/api/user/follow/', user.FollowHandler),
    (r'/api/user/unfollow/', user.Unfollowandler),
    (r'/api/user/star/', user.StarHandler),
    (r'/api/user/follower/', user.FollowerHandler),
    (r'/api/user/following/', user.FollowingHandler),
    (r'/api/user/activity/', user.ActivityHandler),
    (r'/api/note/', note.NoteHandler),
    (r'/api/subnote/', note.SubNoteHandler),
    (r'/api/note/(?P<note_id>[0-9a-f]{32}\Z)?', note.NoteHandler),
    (r'/api/note/comment/(?P<note_id>[0-9a-f]{32}\Z)?', comment.NoteCommentHandler),
    (r'/api/note/comment/star/(?P<comment_id>[0-9a-f]{32}\Z)?', comment.StarCommentHandler),
    (r'/api/note/watch/(?P<note_id>[0-9a-f]{32}\Z)?', note.WatchNoteHandler),
    (r'/api/note/star/(?P<note_id>[0-9a-f]{32}\Z)?', note.StarNoteHandler),
    (r'/api/note/revision/(?P<note_id>[0-9a-f]{32}\Z)?', note.NoteRevisionHandler),
    (r'/api/notebook/?', notebook.NotebooksHandler),
    (r'/api/notebook/(?P<notebook_id>[0-9a-f]{32}\Z)?', notebook.NotebookHandler),
    (r'/api/notebook/watch/(?P<notebook_id>[0-9a-f]{32}\Z)?', notebook.WatchNotebookHandler),
    (r'/api/notebook/pdf/(?P<notebook_id>[0-9a-f]{32}\Z)?', notebook.NotebookPDFHandler),
    (r'/api/organization/checkname/', organization.CheckNameHandler),
    (r'/api/organization/', organization.OrganizationHandler),
    (r'/api/organizations/', organization.OrganizationsHandler),
    (r'/api/organization/notebook/', organization.NotebookHandler),
    (r'/api/organization/people/', organization.PeopleHandler),
    (r'/api/organization/invite/', organization.InviteHandler),
    (r'/api/organization/accept/', organization.AcceptHandler),
    (r'/api/organization/checkmembership/', organization.CheckMembershipHandler),
    (r'/api/upload/', upload.UploadHandler),
    (r'/api/file/(?P<filename>[0-9a-f]{32}.(?:jpg|gif|png)\Z)?', upload.FileHandler)
]

handlers = api_handlers
