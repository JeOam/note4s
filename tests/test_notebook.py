# -*- coding: utf-8 -*-

"""
    test_notebook.py
    ~~~~~~~
"""
import pytest
from .base import BaseHTTPTestCase


class NotebookTestCase(BaseHTTPTestCase):
    def test_create_notebook_without_token(self):
        data = {
            'name': 'test name',
        }
        result = self.post('/api/notebook/', body=data)
        assert isinstance(result, dict)
        assert result["code"] == 401

    @pytest.mark.usefixtures("token")
    def test_create_notebook(self):
        data = {
            'name': 'test name',
        }
        result = self.post('/api/notebook/', body=data, headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert len(result["data"]["id"]) == 32

    @pytest.mark.usefixtures("notebooks", "token")
    def test_get_notebook(self):
        result = self.get('/api/notebook/', headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert len(result["data"]) == 2
        assert result["data"][0]["type"] == "notebook"
        assert len(result["data"][0]["children"]) == 1
        assert len(result["data"][1]["children"]) == 1
        assert result["data"][0]["children"][0]["type"] == "section"
        assert len(result["data"][0]["children"][0]["children"]) == 1
        assert len(result["data"][1]["children"][0]["children"]) == 0
        assert result["data"][0]["children"][0]["children"][0]["type"] == "note"

        notebook_id = result["data"][0]["id"]
        result = self.get(f'/api/notebook/{notebook_id}', headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        notebook = result["data"]
        assert notebook["name"] == "test notebook1"
        assert len(notebook["children"]) == 1
        assert len(notebook["children"][0]["children"]) == 1
        assert notebook["owner"]
        assert notebook["owner_type"] == "user"
        owner = notebook["owner"]
        assert owner["note_count"] == 1
        assert owner["following_count"] == 0
        assert owner["follower_count"] == 0

    @pytest.mark.usefixtures("token")
    def test_get_notebook_without_fixture(self):
        result = self.get('/api/notebook/', headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert len(result["data"]) == 0
