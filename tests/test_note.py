# -*- coding: utf-8 -*-

"""
    test_note.py
    ~~~~~~~
"""
import pytest
from .base import BaseHTTPTestCase


@pytest.mark.usefixtures("token")
class NoteTestCase(BaseHTTPTestCase):
    def test_create_note_without_token(self):
        data = {
            'title': 'test title',
            'content': 'test content'
        }
        result = self.post('/api/note/', body=data)
        assert isinstance(result, dict)
        assert result["code"] == 400

    def test_create_note(self):
        data = {
            'title': 'test title',
            'content': 'test content'
        }
        result = self.post('/api/note/', body=data, headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert len(result["data"]["id"]) == 32
