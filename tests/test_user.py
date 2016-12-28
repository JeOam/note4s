# -*- coding: utf-8 -*-

"""
    test_login.py
    ~~~~~~~
"""
from datetime import datetime
import pytest
from note4s.models import Watch
from .base import BaseHTTPTestCase
from .conftest import session


class UserTestCase(BaseHTTPTestCase):
    @pytest.mark.usefixtures("user")
    def test_login(self):
        data = {
            'email': 'test@test.com',
            'password': '123456'
        }
        result = self.post('/auth/login/', body=data)
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert len(result["data"]) >= 171

    def test_register(self):
        data = {
            'username': 'test',
            'email': 'test@test.com',
            'password': 'admin123'
        }
        result = self.post('/auth/register/', body=data)
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert result["data"]["id"]
        assert result["data"]["email"] == data["email"]
        assert not result["data"].get("password")

    @pytest.mark.usefixtures("user", "another_user", "another_token")
    def test_follow_user(self):
        result = self.post(f'/api/follow/{self.user.id.hex}', body={}, headers={'Authorization': self.another_token})
        assert result["code"] == 200
        assert result["data"] == 1
        watch = session.query(Watch).first()
        assert watch
        assert watch.target_id == self.user.id
        assert watch.user_id == self.another_user.id

    @pytest.mark.usefixtures("note", "token")
    def test_user_contribution(self):
        result = self.get('/api/user/contribution/', params={
            "begin": datetime.now().strftime('%Y-%m-%d'),
            "end": datetime.now().strftime('%Y-%m-%d'),
            "username": self.note.user.username
        }, headers={'Authorization': self.token})
        assert result["code"] == 200
        data = result["data"]
        assert data[datetime.now().strftime('%Y-%m-%d')] == 1
