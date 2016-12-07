# -*- coding: utf-8 -*-

"""
    note.py
    ~~~~~~~
"""
from sqlalchemy import or_, asc
from .base import BaseRequestHandler
from note4s.models import Note, Notebook, Watch, Star, N_TARGET_TYPE


class NoteHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        title = params.get("title")
        content = params.get("content")
        section_id = params.get('section_id')
        notebook_id = params.get('notebook_id')
        note = Note(user=self.current_user,
                    title=title,
                    content=content,
                    section_id=section_id,
                    notebook_id=notebook_id)
        notebook = Notebook(name=title,
                            note_id=note.id,
                            user=self.current_user,
                            parent_id=section_id)
        self.session.add(note)
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
            self.api_fail_response(f'Faied to create sub note: {e}')
        else:
            self.api_success_response(note.to_dict())


class NoteDetailHandler(BaseRequestHandler):
    def get(self, note_id):
        notes = self.session.query(Note). \
            filter(or_(Note.id == note_id,
                       Note.parent_id == note_id)). \
            order_by(asc(Note.created)). \
            all()
        if len(notes) == 0:
            self.api_fail_response(f'Note {note_id} does not exist.')
        else:
            result = {}
            subnotes = []
            for note in notes:
                if note.id.hex == note_id:
                    result = note.to_dict()
                else:
                    subnotes.append(note.to_dict())
            if result.get('id') is None:
                self.api_fail_response(f'Note {note_id} does not exist.')
                return
            notebooks = self.session.query(Notebook). \
                filter(or_(Notebook.id == result.get('notebook_id'),
                           Notebook.id == result.get('section_id'),
                           Notebook.parent_id == result.get('notebook_id'))). \
                all()

            children = []
            for notebook in notebooks:
                if notebook.id == result.get('notebook_id'):
                    result["notebook"] = notebook.to_dict()
                elif notebook.id == result.get('section_id'):
                    result["section"] = notebook.to_dict()
                if notebook.parent_id == result.get('notebook_id'):
                    children.append(notebook.to_dict())
            if result.get('notebook'):
                result["notebook"]["children"] = children
            result["subnotes"] = subnotes
            self.api_success_response(result)

    def put(self, note_id):
        note = self.session.query(Note).filter_by(user=self.current_user, id=note_id).first()
        if note:
            if note.parent_id:
                keys = set(['content'])
            else:
                keys = set(['title', 'content', 'notebook_id', 'section_id'])

            params = self.get_params()
            if params.get('section_id') and note.section_id != params.get('section_id'):
                notebook = self.session.query(Notebook).filter_by(note_id=note.id).first()
                if notebook:
                    notebook.parent_id = params.get('section_id')
                    self.session.add(notebook)

            self.update_modal(note, keys)
            self.session.commit()
            self.api_success_response(note.to_dict())
        else:
            self.api_fail_response(f'Note {note_id} does not exist.')

    def delete(self, note_id):
        notebook = self.session.query(Notebook).filter_by(note_id=note_id).first()
        if notebook:
            self.session.delete(notebook)
        note = self.session.query(Note).filter_by(user=self.current_user, id=note_id).first()
        if note:
            self.session.delete(note)
            self.session.commit()
            self.api_success_response(True)
        else:
            self.api_fail_response(f'Note {note_id} does not exist.')


class WatchNoteHandler(BaseRequestHandler):
    def post(self, note_id):
        note = self.session.query(Note).filter(Note.id == note_id).first()
        if not note:
            self.api_fail_response(f'Note {note_id} does not exist.')
            return

        watch = self.session.query(Watch).filter_by(
            target_id=note_id,
            target_type=N_TARGET_TYPE[1],
            user_id=self.current_user.id
        ).first()
        if watch:
            self.api_success_response(True)
            return

        watch = Watch(target_id=note_id,
                      target_type=N_TARGET_TYPE[1],
                      user_id=self.current_user.id)
        self.session.add(watch)
        self.session.commit()
        self.api_success_response(True)

    def delete(self, note_id):
        note = self.session.query(Note).filter(Note.id == note_id).first()
        if not note:
            self.api_fail_response(f'Note {note_id} does not exist.')
            return
        watch = self.session.query(Watch).filter_by(
            target_id=note_id,
            target_type=N_TARGET_TYPE[1],
            user_id=self.current_user.id
        ).first()
        self.session.delete(watch)
        self.session.commit()
        self.api_success_response(True)


class StarNoteHandler(BaseRequestHandler):
    def post(self, note_id):
        note = self.session.query(Note).filter(Note.id == note_id).first()
        if not note:
            self.api_fail_response(f'Note {note_id} does not exist.')
            return
        star = self.session.query(Star).filter_by(
            target_id=note_id,
            target_type=N_TARGET_TYPE[1],
            user_id=self.current_user.id
        ).first()
        if star:
            self.api_success_response(True)
            return

        star = Star(target_id=note_id,
                    target_type=N_TARGET_TYPE[1],
                    user_id=self.current_user.id)
        self.session.add(star)
        self.session.commit()
        self.api_success_response(True)

    def delete(self, note_id):
        note = self.session.query(Note).filter(Note.id == note_id).first()
        if not note:
            self.api_fail_response(f'Note {note_id} does not exist.')
            return
        star = self.session.query(Star).filter_by(
            target_id=note_id,
            target_type=N_TARGET_TYPE[1],
            user_id=self.current_user.id
        ).first()
        self.session.delete(star)
        self.session.commit()
        self.api_success_response(True)
