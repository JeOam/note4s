# -*- coding: utf-8 -*-

"""
    note.py
    ~~~~~~~
"""
from sqlalchemy import or_, asc
from .base import BaseRequestHandler
from note4s.models import Note, Notebook, Watch, Star, N_TARGET_TYPE, Comment, User
from note4s.service.notify import notify_note_star, notify_note_watch
from note4s.service.feed import feed_new_note, feed_new_subnote, feed_star_note


class NoteHandler(BaseRequestHandler):
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
            user_ids = [note.user_id for note in notes]
            users = self.session.query(User).filter(User.id.in_(user_ids)).all()
            userinfo = {}
            for user in users:
                userinfo[user.id] = user.to_dict(["username", "avatar", "nickname"])
            for note in notes:
                if note.id.hex == note_id:
                    result = note.to_dict()
                    result["user"] = userinfo[note.user_id]
                else:
                    subnote = note.to_dict()
                    subnote["user"] = userinfo[note.user_id]
                    subnotes.append(subnote)
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
                if notebook.id.hex == result.get('notebook_id'):
                    result["notebook"] = notebook.to_dict()
                elif notebook.id.hex == result.get('section_id'):
                    result["section"] = notebook.to_dict()
                if notebook.parent_id and notebook.parent_id.hex == result.get('notebook_id'):
                    children.append(notebook.to_dict())
            if result.get('notebook'):
                result["notebook"]["children"] = children
            result["subnotes"] = subnotes

            watch_count = self.session.query(Watch).filter_by(
                target_id=note_id,
                target_type=N_TARGET_TYPE[1]
            ).count()
            is_watch = self.session.query(Watch).filter_by(
                target_id=note_id,
                target_type=N_TARGET_TYPE[1],
                user_id=self.current_user.id
            ).first()
            star_count = self.session.query(Star).filter_by(
                target_id=note_id,
                target_type=N_TARGET_TYPE[1]
            ).count()
            is_star = self.session.query(Star).filter_by(
                target_id=note_id,
                target_type=N_TARGET_TYPE[1],
                user_id=self.current_user.id
            ).first()

            comment_count = self.session.query(Comment).filter_by(
                note_id=note_id,
            ).count()

            result['watch_count'] = watch_count
            result['is_watch'] = bool(is_watch)
            result['star_count'] = star_count
            result['is_star'] = bool(is_star)
            result['comment_count'] = comment_count
            self.api_success_response(result)

    def post(self, *args, **kwargs):
        params = self.get_params()
        title = params.get("title")
        content = params.get("content")
        section_id = params.get('section_id')
        notebook_id = params.get('notebook_id')
        if not notebook_id or not section_id:
            self.api_fail_response(f'Notebook or Section is required.')
            return

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
        feed_new_note(user_id=self.current_user.id,
                      note_id=note.id,
                      note_title=note.title,
                      notebook_id=notebook_id,
                      session=self.session)
        self.api_success_response(note.to_dict())

    def put(self, note_id):
        note = self.session.query(Note).filter_by(user=self.current_user, id=note_id).first()
        if note:
            if note.parent_id:
                keys = set(['content'])
            else:
                keys = set(['title', 'content', 'notebook_id', 'section_id'])

            params = self.get_params()
            if (params.get('section_id') and note.section_id != params.get('section_id')) or \
                    params.get('title'):
                notebook = self.session.query(Notebook).filter_by(note_id=note.id).first()
                if notebook:
                    if params.get('title'):
                        notebook.name = params.get('title')
                    if params.get('section_id'):
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


class SubNoteHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        content = params.get("content")
        parent_id = params.get('parent_id')
        note = Note(user=self.current_user,
                    content=content,
                    parent_id=parent_id)
        self.session.add(note)
        self.session.commit()
        feed_new_subnote(user_id=self.current_user.id,
                         note_id=parent_id,
                         subnote_id=note.id,
                         session=self.session)
        result = note.to_dict()
        result["user"] = self.current_user.to_dict(["username", "avatar", "nickname"])
        self.api_success_response(result)


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
        watch_count = self.session.query(Watch).filter_by(
            target_id=note_id,
            target_type=N_TARGET_TYPE[1]
        ).count()
        if watch:
            self.api_success_response(watch_count)
            return

        watch = Watch(target_id=note_id,
                      target_type=N_TARGET_TYPE[1],
                      user_id=self.current_user.id)
        self.session.add(watch)
        self.session.commit()
        if note.user_id != self.current_user.id:
            notify_note_watch(
                note_owner_id=note.user_id,
                note_id=note.id,
                note_title=note.title,
                sender_id=self.current_user.id,
                session=self.session
            )
        self.api_success_response(watch_count + 1)

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
        star_count = self.session.query(Star).filter_by(
            target_id=note_id,
            target_type=N_TARGET_TYPE[1]
        ).count()
        if star:
            self.api_success_response(star_count)
            return

        star = Star(target_id=note_id,
                    target_type=N_TARGET_TYPE[1],
                    user_id=self.current_user.id)
        self.session.add(star)
        self.session.commit()
        if note.user_id != self.current_user.id:
            notify_note_star(
                note_owner_id=note.user_id,
                note_id=note.id,
                note_title=note.title,
                sender_id=self.current_user.id,
                session=self.session
            )
        feed_star_note(
            user_id=self.current_user.id,
            note_id=note.id,
            note_title=note.title,
            notebook_id=note.notebook_id,
            session=self.session
        )
        self.api_success_response(star_count + 1)

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
