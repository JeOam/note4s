# -*- coding: utf-8 -*-

"""
    test_nofity.py
    ~~~~~~~
"""
import pytest
from .base import BaseHTTPTestCase


@pytest.mark.usefixtures("user", "token", "another_user", "another_token")
class NofiticationTestCase(BaseHTTPTestCase):
    def test_create_note_nofity(self):
        result = self.post(f'/api/follow/{self.user.id.hex}', body={}, headers={'Authorization': self.another_token})
        assert result["code"] == 200
        data = {
            'title': 'test title',
            'content': 'test content'
        }
        result = self.post('/api/note/', body=data, headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert len(result["data"]["id"]) == 32
