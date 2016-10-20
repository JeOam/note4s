# -*- coding: utf-8 -*-

"""
    note.py
    ~~~~~~~
"""
from sqlalchemy.orm import exc
from .base import BaseRequestHandler
from note4s.models import Note


class NoteHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        title = params.get("title")
        content = params.get("content")
        note = Note(user=self.current_user,
                    title=title,
                    content=content)
        self.session.add(note)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            self.api_fail_response("Failed to create note.")
        else:
            self.api_success_response(note.to_dict())


class NoteDetailHandler(BaseRequestHandler):
    def get(self, note_id):
        try:
            note = self.session.query(Note).filter_by(id=note_id).one()
        except exc.NoResultFound as e:
            self.api_fail_response("Note {} does not exist.".format(id))
        else:
            self.api_success_response(note.to_dict())
