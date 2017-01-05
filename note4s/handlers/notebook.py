# -*- coding: utf-8 -*-

"""
    notebook.py
    ~~~~~~~
"""
from sqlalchemy.orm import exc
from .base import BaseRequestHandler
from note4s.models import Notebook


class NotebookHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        notebooks = self.session.query(Notebook).filter_by(user=self.current_user).all()
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
                notebook_info["type"] = "notebook"
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

    def delete(self, notebook_id):
        try:
            notebook = self.session.query(Notebook).filter_by(id=notebook_id).one()
        except exc.NoResultFound as e:
            self.api_fail_response(f'Notebook {notebook_id} does not exist.')
        else:
            self.session.delete(notebook)
            self.session.commit()
            self.api_success_response(notebook.to_dict())