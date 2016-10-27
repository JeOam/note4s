# -*- coding: utf-8 -*-

"""
    note.py
    ~~~~~~~
"""
from sqlalchemy.orm import exc
from sqlalchemy import or_, asc
from .base import BaseRequestHandler
from note4s.models import Note, Notebook


class NoteHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        title = params.get("title")
        content = params.get("content")
        notebook_id = params.get('notebook_id')
        note = Note(user=self.current_user,
                    title=title,
                    content=content,
                    notebook_id=notebook_id)
        self.session.add(note)
        self.session.commit()
        notebook = Notebook(name=title,
                            note_id=note.id,
                            user=self.current_user,
                            parent_id=notebook_id)
        self.session.add(notebook)
        self.session.commit()
        self.api_success_response(note.to_dict())


class SubNoteHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        content = params.get("content")
        parent_id = params.get('parent_id')
        note = Note(user=self.current_user,
                    content=content,
                    parent_id=parent_id)
        self.session.add(note)
        try:
            self.session.commit()
        except Exception as e:
            self.api_fail_response("Faied to create sub note: {}".format(e))
        else:
            self.api_success_response(note.to_dict())


class NoteDetailHandler(BaseRequestHandler):
    def get(self, note_id):
        notes = self.session.query(Note).\
            filter(or_(Note.id == note_id,
                       Note.parent_id == note_id)). \
            order_by(asc(Note.created)).\
            all()
        if len(notes) == 0:
            self.api_fail_response("Note {} does not exist.".format(note_id))
        else:
            result = {}
            subnotes = []
            for note in notes:
                if note.id == note_id:
                    result = note.to_dict()
                else:
                    subnotes.append(note.to_dict())

            result["subnotes"] = subnotes
            self.api_success_response(result)
