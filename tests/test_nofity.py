# -*- coding: utf-8 -*-

"""
    test_nofity.py
    ~~~~~~~
"""
import pytest
from .base import BaseHTTPTestCase


@pytest.mark.usefixtures("token")
class NofiticationTestCase(BaseHTTPTestCase):
    def test_create_note_nofity(self):
        data = {
            'title': 'test title',
            'content': 'test content'
        }
        result = self.post('/api/note/', body=data, headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert len(result["data"]["id"]) == 32
