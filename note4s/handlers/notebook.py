# -*- coding: utf-8 -*-

"""
    notebook.py
    ~~~~~~~
"""
from sqlalchemy import or_, and_
from .base import BaseRequestHandler
from note4s.models import Notebook, OWNER_TYPE, User, Organization, \
    Watch, N_TARGET_TYPE, Note, Membership, O_ROLE
from note4s.service.feed import feed_new_notebook, feed_notebook_watch
from note4s.service.notify import notify_notebook_watch


class NotebooksHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        username = self.get_argument("username", None)
        useronly = self.get_argument("useronly", False)
        if username:
            user = self.session.query(User).filter_by(username=username).first()
            if not user:
                self.api_fail_response(f'User {username} does not exist.')
                return
        else:
            user = self.current_user
        if useronly:
            notebooks = self.session.query(Notebook).filter(
                Notebook.owner_id == user.id,
                Notebook.owner_type == OWNER_TYPE[0]
            ).all()
        else:
            memberships = self.session.query(Membership).filter(
                Membership.user_id == user.id,
                Membership.role != O_ROLE[2]
            ).all()
            organization_ids = [membership.organization_id for membership in memberships]
            notebooks = self.session.query(Notebook).filter(
                or_(
                    and_(
                        Notebook.owner_id == user.id,
                        Notebook.owner_type == OWNER_TYPE[0]
                    ), and_(
                        Notebook.owner_id.in_(organization_ids),
                        Notebook.owner_type == OWNER_TYPE[1]
                    )
                )
            ).all()
        temp = {}
        result = []
        for notebook in notebooks:
            if notebook.parent_id:
                if temp.get(notebook.parent_id.hex):
                    temp[notebook.parent_id.hex].append(notebook.to_dict())
                else:
                    temp[notebook.parent_id.hex] = [notebook.to_dict()]
            else:
                notebook_info = notebook.to_dict()
                watch_count = self.session.query(Watch).filter_by(
                    target_id=notebook.id,
                    target_type=N_TARGET_TYPE[3]
                ).count()
                notebook_info["type"] = "notebook"
                notebook_info["watch_count"] = watch_count
                result.append(notebook_info)
        for notebook in result:
            sections = temp.get(notebook["id"], [])
            notebook["children"] = []
            for section in sections:
                section["type"] = "section"
                notes = temp.get(section["id"], [])
                for note in notes:
                    note["type"] = "note"
                section["children"] = notes
                notebook["children"].append(section)
        self.api_success_response(result)

    def post(self, *args, **kwargs):
        params = self.get_params()
        name = params.get("name")
        parent_id = params.get('parent_id')
        organization_id = params.get('organization_id')
        if organization_id:
            notebook = Notebook(owner_id=organization_id,
                                owner_type=OWNER_TYPE[1],
                                name=name,
                                parent_id=parent_id)
        else:
            notebook = Notebook(owner_id=self.current_user.id,
                                owner_type=OWNER_TYPE[0],
                                name=name,
                                parent_id=parent_id)
        self.session.add(notebook)
        self.session.commit()
        if not parent_id and not organization_id:
            feed_new_notebook(
                user_id=self.current_user.id,
                notebook_id=notebook.id,
                session=self.session
            )
        self.api_success_response(notebook.to_dict())


class NotebookHandler(BaseRequestHandler):
    def get(self, notebook_id):
        notebook = self.session.query(Notebook).filter_by(id=notebook_id).first()
        if not notebook:
            self.api_fail_response(f'Notebook {notebook_id} does not exist.')
            return
        if notebook.owner_type == OWNER_TYPE[0]:
            owner = self.session.query(User).filter_by(id=notebook.owner_id).first()
        else:
            owner = self.session.query(Organization).filter_by(id=notebook.owner_id).first()
        if not owner:
            self.api_fail_response(f'Notebook {notebook_id} does not belong to any user/organization.')
            return
        owner_info = owner.to_dict()
        notebook_ids = self.session.query(Notebook.id).filter(
            Notebook.owner_id == owner.id,
            Notebook.owner_type == notebook.owner_type,
            Notebook.parent_id.is_(None)
        ).all()
        notebook_ids = [notebook[0] for notebook in notebook_ids]
        notebook_count = len(notebook_ids)
        note_count = self.session.query(Note).filter(
            Note.notebook_id.in_(notebook_ids),
            Note.parent_id.is_(None)
        ).count()
        owner_info["notebook_count"] = notebook_count
        owner_info["note_count"] = note_count
        if notebook.owner_type == OWNER_TYPE[0]:
            following_count = self.session.query(Watch).filter_by(
                target_type=N_TARGET_TYPE[0],
                user_id=owner.id,
            ).count()
            follower_count = self.session.query(Watch).filter_by(
                target_type=N_TARGET_TYPE[0],
                target_id=owner.id,
            ).count()
            owner_info["following_count"] = following_count
            owner_info["follower_count"] = follower_count
        else:
            watch_count = self.session.query(Watch).filter(
                Watch.target_id.in_(notebook_ids),
                Watch.target_type == N_TARGET_TYPE[3]
            ).count()
            owner_info["watch_count"] = watch_count

        notebook_info = notebook.to_dict()
        notebook_info["owner"] = owner_info
        notebook_info["owner_type"] = notebook.owner_type
        is_watch = self.session.query(Watch.id).filter(
            Watch.target_id == notebook.id,
            Watch.target_type == N_TARGET_TYPE[3],
            Watch.user_id == self.current_user.id
        ).count()
        notebook_info["is_watch"] = True if is_watch else False
        watch_count = self.session.query(Watch.id).filter(
            Watch.target_id == notebook.id,
            Watch.target_type == N_TARGET_TYPE[3],
        ).count()
        notebook_info["watch_count"] = watch_count
        sections = self.session.query(Notebook).filter(
            Notebook.parent_id == notebook.id
        ).all()
        notebook_info["children"] = []
        if sections:
            section_ids = [section.id for section in sections]
            notes = self.session.query(Notebook).filter(
                Notebook.parent_id.in_(section_ids)
            ).all()
            section_info = {}
            for index, section in enumerate(sections):
                section_info[section.id] = index
                section_dict = section.to_dict()
                section_dict["children"] = []
                notebook_info["children"].append(section_dict)
            for note in notes:
                index = section_info[note.parent_id]
                notebook_info["children"][index]["children"].append(note.to_dict())
        self.api_success_response(notebook_info)

    def delete(self, notebook_id):
        notebook = self.session.query(Notebook).filter_by(id=notebook_id).first()
        if not notebook:
            self.api_fail_response(f'Notebook {notebook_id} does not exist.')
            return
        children_notebooks = self.session.query(Notebook).filter_by(parent_id=notebook_id).count()
        if children_notebooks:
            self.api_fail_response('Notebook cannot be deleted because of nonempty')
            return
        section_notes = self.session.query(Note).filter(Note.section_id == notebook_id).all()
        for note in section_notes:
            note.section_id = None
            self.session.add(note)
        notebook_notes = self.session.query(Note).filter(Note.notebook_id == notebook_id).all()
        for note in notebook_notes:
            note.notebook_id = None
            note.section_id = None
            self.session.add(note)
        self.session.delete(notebook)
        self.session.commit()
        self.api_success_response(notebook.to_dict())


class WatchNotebookHandler(BaseRequestHandler):
    def post(self, notebook_id):
        notebook = self.session.query(Notebook).filter(Notebook.id == notebook_id).first()
        if not notebook:
            self.api_fail_response(f'Notebook {notebook_id} does not exist.')
            return

        watch = self.session.query(Watch).filter_by(
            target_id=notebook_id,
            target_type=N_TARGET_TYPE[3],
            user_id=self.current_user.id
        ).first()
        watch_count = self.session.query(Watch).filter_by(
            target_id=notebook_id,
            target_type=N_TARGET_TYPE[3]
        ).count()
        if watch:
            self.api_success_response(watch_count)
            return

        watch = Watch(target_id=notebook_id,
                      target_type=N_TARGET_TYPE[3],
                      user_id=self.current_user.id)
        self.session.add(watch)
        self.session.commit()
        if notebook.owner_type == OWNER_TYPE[0] and \
                        notebook.owner_id != self.current_user.id:
            notify_notebook_watch(
                notebook_owner_id=notebook.owner_id,
                notebook_id=notebook.id,
                notebook_name=notebook.name,
                sender_id=self.current_user.id,
                session=self.session
            )
        feed_notebook_watch(
            notebook_id=notebook.id,
            user_id=self.current_user.id,
            session=self.session
        )
        self.api_success_response(watch_count + 1)

    def delete(self, notebook_id):
        notebook = self.session.query(Notebook).filter(Notebook.id == notebook_id).first()
        if not notebook:
            self.api_fail_response(f'Notebook {notebook} does not exist.')
            return
        watch = self.session.query(Watch).filter_by(
            target_id=notebook_id,
            target_type=N_TARGET_TYPE[3],
            user_id=self.current_user.id
        ).first()
        self.session.delete(watch)
        self.session.commit()
        self.api_success_response(True)
