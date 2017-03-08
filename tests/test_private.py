# -*- coding: utf-8 -*-

"""
    test_private.py
    ~~~~~~~
"""
import pytest
from .base import BaseHTTPTestCase


class PublicTestCase(BaseHTTPTestCase):
    @pytest.mark.usefixtures("notebook")
    def test_visitor_public_notebook(self):
        result = self.get(f'/api/notebook/{self.notebook.id.hex}')
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert result["data"]["id"]

    @pytest.mark.usefixtures("notebook", "another_token")
    def test_other_user_public_notebook(self):
        result = self.get(f'/api/notebook/{self.notebook.id.hex}', headers={'Authorization': self.another_token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert result["data"]["id"]

    @pytest.mark.usefixtures("notebook", "token")
    def test_onwer_public_notebook(self):
        result = self.get(f'/api/notebook/{self.notebook.id.hex}',
                          headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert result["data"]["id"]

    @pytest.mark.usefixtures("note")
    def test_visitor_public_notebook(self):
        result = self.get(f'/api/note/{self.note.id.hex}')
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert result["data"]["id"]

    @pytest.mark.usefixtures("note", "another_token")
    def test_other_user_public_notebook(self):
        result = self.get(f'/api/note/{self.note.id.hex}', headers={'Authorization': self.another_token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert result["data"]["id"]

    @pytest.mark.usefixtures("note", "token")
    def test_onwer_public_notebook(self):
        result = self.get(f'/api/note/{self.note.id.hex}',
                          headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert result["data"]["id"]


class PrivateTestCase(BaseHTTPTestCase):
    @pytest.mark.usefixtures("private_notebook")
    def test_visitor_private_notebook(self):
        result = self.get(f'/api/notebook/{self.private_notebook.id.hex}')
        assert isinstance(result, dict)
        assert result["code"] == 404

    @pytest.mark.usefixtures("private_notebook", "token")
    def test_other_user_private_notebook(self):
        result = self.get(f'/api/notebook/{self.private_notebook.id.hex}', headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 404

    @pytest.mark.usefixtures("private_notebook", "another_token")
    def test_onwer_private_notebook(self):
        result = self.get(f'/api/notebook/{self.private_notebook.id.hex}',
                          headers={'Authorization': self.another_token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert result["data"]["id"]

    @pytest.mark.usefixtures("private_note")
    def test_visitor_private_note(self):
        result = self.get(f'/api/note/{self.private_note.id.hex}')
        assert isinstance(result, dict)
        assert result["code"] == 404

    @pytest.mark.usefixtures("private_note", "token")
    def test_other_user_private_note(self):
        result = self.get(f'/api/note/{self.private_note.id.hex}', headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 404

    @pytest.mark.usefixtures("private_note", "another_token")
    def test_onwer_private_note(self):
        result = self.get(f'/api/note/{self.private_note.id.hex}',
                          headers={'Authorization': self.another_token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert result["data"]["id"]
