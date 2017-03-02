# -*- coding: utf-8 -*-

"""
    test_login.py
    ~~~~~~~
"""
import shutil
from datetime import datetime
import pytest
from note4s.models import Watch, N_TARGET_TYPE, Notification, Activity
from note4s import settings
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
        shutil.rmtree(settings.GIT_DIR + result["data"]["id"], ignore_errors=True)


    @pytest.mark.usefixtures("note", "user", "token", "another_user", "another_token")
    def test_follow_user(self):
        result = self.post(
            '/api/user/follow/',
            body={"username": self.user.username},
            headers={'Authorization': self.another_token}
        )
        assert result["code"] == 200
        assert result["data"] is True
        watch = session.query(Watch).filter_by(
            target_id=self.user.id,
            target_type=N_TARGET_TYPE[0],
            user_id=self.another_user.id
        ).count()
        assert watch == 1
        notification = session.query(Notification).filter_by(
            target_id=self.user.id,
            target_type=N_TARGET_TYPE[0],
            sender_id=self.another_user.id
        ).one()
        assert notification

        data = {
            'title': 'test title',
            'content': 'test content',
            "section_id": self.note.section_id.hex,
            "notebook_id": self.note.notebook_id.hex
        }
        result = self.post('/api/note/', body=data, headers={'Authorization': self.token})
        assert result["code"] == 200
        activity = session.query(Activity).filter_by(
            target_id=result["data"]["id"],
            target_type=N_TARGET_TYPE[1],
            user_id=self.user.id
        ).one()
        assert activity

        result = self.post(
            '/api/user/unfollow/',
            body={"username": self.user.username},
            headers={'Authorization': self.another_token}
        )
        assert result["code"] == 200
        assert result["data"] is True
        watch = session.query(Watch).filter_by(
            target_id=self.user.id,
            target_type=N_TARGET_TYPE[0],
            user_id=self.another_user.id
        ).count()
        assert watch == 0

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
