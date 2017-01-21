# -*- coding: utf-8 -*-

"""
    notebook.py
    ~~~~~~~
"""
from sqlalchemy.orm import exc
from .base import BaseRequestHandler
from note4s.models import Notebook, User, Watch, N_TARGET_TYPE, Note


class NotebooksHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        username = self.get_argument("username", None)
        if username:
            user = self.session.query(User).filter_by(username=username).first()
            if not user:
                self.api_fail_response(f'User {username} does not exist.')
                return
        else:
            user = self.current_user
        notebooks = self.session.query(Notebook).filter_by(user=user).all()
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
        notebook = Notebook(user=self.current_user,
                            name=name,
                            parent_id=parent_id)
        self.session.add(notebook)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            self.api_fail_response("Failed to create notebook.")
        else:
            self.api_success_response(notebook.to_dict())


class NotebookHandler(BaseRequestHandler):
    def get(self, notebook_id):
        notebook = self.session.query(Notebook).filter_by(id=notebook_id).first()
        if not notebook:
            self.api_fail_response(f'Notebook {notebook_id} does not exist.')
            return
        user = self.session.query(User).filter_by(id=notebook.user_id).first()
        if not user:
            self.api_fail_response(f'Notebook {notebook_id} does not belong to any user.')
            return
        notebook_count = self.session.query(Notebook).filter_by(user=user, parent_id=None).count()
        note_count = self.session.query(Note).filter_by(user_id=user.id).count()
        following_count = self.session.query(Watch).filter_by(
            target_type=N_TARGET_TYPE[0],
            user_id=user.id,
        ).count()
        follower_count = self.session.query(Watch).filter_by(
            target_id=user.id,
            target_type=N_TARGET_TYPE[0]
        ).count()
        userinfo = user.to_dict()
        userinfo["notebook_count"] = notebook_count
        userinfo["note_count"] = note_count
        userinfo["following_count"] = following_count
        userinfo["follower_count"] = follower_count
        notebook_info = notebook.to_dict()
        notebook_info["user"] = userinfo

        sections = self.session.query(Notebook).filter(
            Notebook.parent_id == notebook.id
        ).all()
        section_ids = [section.id for section in sections]
        notes = self.session.query(Notebook).filter(
            Notebook.parent_id.in_(section_ids)
        ).all()
        notebook_info["children"] = []
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
        self.session.delete(notebook)
        self.session.commit()
        self.api_success_response(notebook.to_dict())
