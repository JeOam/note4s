# -*- coding: utf-8 -*-

"""
    test_comment.py
    ~~~~~~~
"""
import pytest
from note4s.models import Comment
from .base import BaseHTTPTestCase
from .conftest import session

class CommentTestCase(BaseHTTPTestCase):

    @pytest.mark.usefixtures("note", "token")
    def test_note_comment_detail(self):
        result = self.get(f'/api/note/comment/{self.note.id.hex}', headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert result["data"]["note"]["id"] == self.note.id.hex
        assert result["data"]["comments"] == []

    @pytest.mark.usefixtures("note", "user", "token")
    def test_create_comment(self):
        params = {
            "content": "test comment"
        }
        result = self.post(f'/api/note/comment/{self.note.id.hex}', body=params, headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        data = result["data"]
        assert data["content"] == "test comment"
        assert data["note_id"] == self.note.id.hex
        assert data["user_id"] == self.user.id.hex