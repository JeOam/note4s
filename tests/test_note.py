# -*- coding: utf-8 -*-

"""
    test_note.py
    ~~~~~~~
"""
import pytest
from note4s.models import Watch, Star, Activity
from .base import BaseHTTPTestCase
from .conftest import session

class NoteTestCase(BaseHTTPTestCase):
    def test_create_note_without_token(self):
        data = {
            'title': 'test title',
            'content': 'test content',
        }
        result = self.post('/api/note/', body=data)
        assert isinstance(result, dict)
        assert result["code"] == 401

    @pytest.mark.usefixtures("token", "note")
    def test_create_note(self):
        data = {
            'title': 'test title',
            'content': 'test content',
            "section_id": self.note.section_id.hex,
            "notebook_id": self.note.notebook_id.hex
        }
        result = self.post('/api/note/', body=data, headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert len(result["data"]["id"]) == 32

        result = self.get('/api/user/activity/', headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert len(result["data"]) == 1
        assert result["data"][0]["target_type"] == "note"
        assert result["data"][0]["user"]

    def test_note_detail_url(self):
        result = self.get('/api/note/123')
        assert result == '<html><title>404: Not Found</title><body>404: Not Found</body></html>'

        result = self.get('/api/note/123456789012345678901234567890123')
        assert result == '<html><title>404: Not Found</title><body>404: Not Found</body></html>'

    @pytest.mark.usefixtures("note", "token")
    def test_note_detail(self):
        result = self.get(f'/api/note/{self.note.id.hex}', headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert len(result["data"]["id"]) == 32
        assert result['data']['section_id']
        assert result['data']['section']
        assert result['data']['section']['name']
        assert result['data']['notebook_id']
        assert result['data']['notebook']['name']
        assert result['data']['is_watch'] is False
        assert result['data']['watch_count'] == 0
        assert result['data']['is_star'] is False
        assert result['data']['star_count'] == 0

    @pytest.mark.usefixtures("note", "another_user", "another_token", "token")
    def test_watch_note(self):
        result = self.post(f'/api/note/watch/{self.note.id.hex}', body={}, headers={'Authorization': self.another_token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert result["data"] == 1
        watch = session.query(Watch).filter_by(
            target_id=self.note.id,
            target_type="note",
            user_id=self.another_user.id
        ).one()
        assert watch
        session.commit()

        result = self.post('/api/subnote/',
                           body={'content': 'test sub note',
                                 'parent_id': self.note.id.hex},
                           headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        session.commit()
        activity = session.query(Activity).filter_by(target_id=self.note.id, action="new subnote").one()
        assert activity


    @pytest.mark.usefixtures("note", "another_user", "another_token")
    def test_star_note(self):
        result = self.post(f'/api/note/star/{self.note.id.hex}', body={}, headers={'Authorization': self.another_token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert result["data"] == 1
        star = session.query(Star).first()
        assert star
        assert star.target_id == self.note.id
        assert star.user_id == self.another_user.id

        result = self.get('/api/user/star/',
                          params={'username': self.another_user.username},
                          headers={'Authorization': self.another_token})
        assert result["code"] == 200
        assert result["data"][0]["id"]