# -*- coding: utf-8 -*-

"""
    notebook.py
    ~~~~~~~
"""
from .base import BaseRequestHandler
from note4s.models import Notebook

class NotebookHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        name = params.get("name")
        notebook = Notebook(user=self.current_user,
                            name=name)
        self.session.add(notebook)
        try:
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            self.api_fail_response("Failed to create notebook.")
        else:
            self.api_success_response(notebook.to_dict())


    def get(self, *args, **kwargs):
        notebooks = self.session.query(Notebook).filter_by(user=self.current_user).all()
        temp = {}
        result = []
        for notebook in notebooks:
            if notebook.parent_id:
                if temp.get(notebook.parent_id):
                    temp[notebook.parent_id].push(notebook.to_dict())
                else:
                    temp[notebook.parent_id] = [notebook.to_dict()]
            else:
                result.append(notebook.to_dict())
        for notebook in result:
            sections = temp.get(notebook["id"], [])
            notebook["children"] = []
            for section in sections:
                notes = temp.get(section["id"], [])
                section["children"] = notes
                notebook["children"].append(section)

        self.api_success_response(result)

