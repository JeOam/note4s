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

    def test_note_detail_url(self):
        result = self.get('/api/note/123')
        assert result == '<html><title>404: Not Found</title><body>404: Not Found</body></html>'

        result = self.get('/api/note/123456789012345678901234567890123')
        assert result == '<html><title>404: Not Found</title><body>404: Not Found</body></html>'

    @pytest.mark.usefixtures("note")
    def test_note_detail(self):
        result = self.get('/api/note/{}'.format(self.note.id))
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert len(result["data"]["id"]) == 32