# -*- coding: utf-8 -*-

"""
    note.py
    ~~~~~~~
"""
from sqlalchemy import or_, asc
from .base import BaseRequestHandler
from note4s.models import Note, Notebook, OWNER_TYPE, \
    Watch, Star, N_TARGET_TYPE, Comment, User, Membership, O_ROLE
from note4s.service.notify import notify_note_star, notify_note_watch
from note4s.service.feed import feed_new_note, feed_new_subnote, feed_star_note
from note4s.service.git import edit_git_note, delete_git_note, \
    get_note_revision_count, get_note_history


class NoteHandler(BaseRequestHandler):
    def get(self, note_id):
        note = self.session.query(Note).filter_by(id=note_id).first()
        if not note:
            self.api_fail_response(f'Note {note_id} does not exist.', 404)
            return
        notebook = self.session.query(Notebook).filter_by(id=note.notebook_id).first()
        if not notebook:
            self.api_fail_response(f'Note does not own to any notebook.')
            return
        if notebook.private:
            if not self.current_user:
                self.api_fail_response(f'Note {note_id} does not exist', 404)
                return
            if notebook.owner_type == OWNER_TYPE[0]:
                if notebook.owner_id != self.current_user.id:
                    self.api_fail_response(f'Note {note_id} does not exist', 404)
                    return
            else:
                membership = self.session.query(Membership).filter(
                    Membership.organization_id == notebook.owner_id,
                    Membership.user_id == self.current_user.id,
                    Membership.role != O_ROLE[3]
                ).count()
                if membership == 0:
                    self.api_fail_response(f'Note {note_id} does not exist', 404)
                    return
        notes = self.session.query(Note). \
            filter(or_(Note.id == note_id,
                       Note.parent_id == note_id)). \
            order_by(asc(Note.created)). \
            all()
        result = {}
        subnotes = []
        user_ids = [note.user_id for note in notes]
        users = self.session.query(User).filter(User.id.in_(user_ids)).all()
        userinfo = {}
        for user in users:
            userinfo[user.id] = user.to_dict(["username", "avatar", "nickname"])
        for note in notes:
            revision_count = get_note_revision_count(
                user_id=note.user_id.hex,
                note_id=note.id.hex
            )
            if note.id.hex == note_id:
                result = note.to_dict()
                result["user"] = userinfo[note.user_id]
                result["revision_count"] = revision_count
            else:
                subnote = note.to_dict()
                subnote["user"] = userinfo[note.user_id]
                subnote["revision_count"] = revision_count
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
        star_count = self.session.query(Star).filter_by(
            target_id=note_id,
            target_type=N_TARGET_TYPE[1]
        ).count()
        if self.current_user:
            is_watch = self.session.query(Watch).filter_by(
                target_id=note_id,
                target_type=N_TARGET_TYPE[1],
                user_id=self.current_user.id
            ).first()
            is_star = self.session.query(Star).filter_by(
                target_id=note_id,
                target_type=N_TARGET_TYPE[1],
                user_id=self.current_user.id
            ).first()
        else:
            is_watch = None
            is_star = None
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
        private = params.get('private', False)
        if not notebook_id or not section_id:
            self.api_fail_response('Notebook or Section is required.')
            return

        notebook = self.session.query(Notebook).filter_by(id=notebook_id).first()
        if not notebook:
            self.api_fail_response('notebook_id is invalid.')
            return

        note = Note(user=self.current_user,
                    title=title,
                    content=content,
                    section_id=section_id,
                    notebook_id=notebook_id)
        notebook = Notebook(name=title,
                            note_id=note.id,
                            parent_id=section_id,
                            owner_id=notebook.owner_id,
                            owner_type=notebook.owner_type)
        self.session.add(note)
        self.session.add(notebook)
        self.session.commit()
        if not private:
            feed_new_note(user_id=self.current_user.id,
                          note_id=note.id,
                          note_title=note.title,
                          notebook_id=notebook_id,
                          session=self.session)
        edit_git_note(user_id=self.current_user.id.hex,
                      note_id=note.id.hex,
                      content=content,
                      author=self.current_user.username)
        self.api_success_response(note.to_dict())

    def put(self, note_id):
        note = self.session.query(Note).filter_by(user=self.current_user, id=note_id).first()
        if note:
            old_content = note.content
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
            result = note.to_dict()
            if note.content != old_content:
                user = self.session.query(User).filter_by(id=note.user_id).first()
                if user:
                    edit_git_note(user_id=note.user_id.hex,
                                  note_id=note.id.hex,
                                  content=note.content,
                                  author=user.username)
                    result["revision_count"] = get_note_revision_count(
                        user_id=note.user_id.hex,
                        note_id=note.id.hex
                    )
            self.api_success_response(result)
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
            delete_git_note(user_id=note.user_id.hex,
                            note_id=note.id.hex)
            self.api_success_response(True)
        else:
            self.api_fail_response(f'Note {note_id} does not exist.')


class SubNoteHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        content = params.get("content")
        parent_id = params.get('parent_id')
        if not parent_id:
            self.api_fail_response(f'parent_id is required.')
            return
        parent_note = self.session.query(Note).filter_by(id=parent_id).first()
        if not parent_note:
            self.api_fail_response(f'parent_id is invalid.')
            return
        note = Note(user=self.current_user,
                    content=content,
                    parent_id=parent_id,
                    section_id=parent_note.section_id,
                    notebook_id=parent_note.notebook_id)
        self.session.add(note)
        self.session.commit()
        feed_new_subnote(user_id=self.current_user.id,
                         note_id=parent_id,
                         subnote_id=note.id,
                         session=self.session)
        edit_git_note(user_id=self.current_user.id.hex,
                      note_id=note.id.hex,
                      content=content,
                      author=self.current_user.username)
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


class NoteRevisionHandler(BaseRequestHandler):
    def get(self, note_id):
        note = self.session.query(Note).filter(Note.id == note_id).first()
        if not note:
            self.api_fail_response(f'Note {note_id} does not exist.')
            return
        diffs = get_note_history(
            user_id=note.user_id.hex,
            note_id=note.id.hex
        )
        self.api_success_response(diffs)
