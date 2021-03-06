# -*- coding: utf-8 -*-

"""
    test_nofity.py
    ~~~~~~~
"""
import pytest
from note4s.models import Notification, UserNotification
from .base import BaseHTTPTestCase
from .conftest import session


class NofiticationTestCase(BaseHTTPTestCase):
    @pytest.mark.usefixtures("user", "token", "note", "another_user", "another_token")
    def test_star_note_notify_owner(self):
        result = self.post(f'/api/note/star/{self.note.id.hex}', body={}, headers={'Authorization': self.another_token})
        assert result["code"] == 200
        notification = session.query(Notification).filter_by(target_id=self.note.id).one()
        user_notification = session.query(UserNotification).filter_by(user_id=self.user.id).one()
        assert notification
        assert notification.target_id == self.note.id
        assert notification.target_type == 'note'
        assert notification.action == 'star'
        assert notification.type == 'remind'
        assert notification.sender_id == self.another_user.id
        assert notification.target_desc == self.note.title
        assert user_notification
        assert user_notification.notification_id == notification.id
        assert user_notification.is_read is False

        result = self.get(f'/api/user/notification/', headers={'Authorization': self.token})
        assert result["code"] == 200
        data = result["data"]
        assert data["unread_count"] == 1
        assert len(data["generals"]) == 0
        assert len(data["follows"]) == 0
        assert len(data["stars"]) == 1
        _notification = data["stars"][0]
        assert _notification["is_read"] is False
        assert _notification["target_id"] == self.note.id.hex
        assert _notification["target_type"] == 'note'
        assert _notification["action"] == 'star'

    @pytest.mark.usefixtures("user", "token", "note", "another_user", "another_token")
    def test_watch_note_notify_owner(self):
        result = self.post(f'/api/note/watch/{self.note.id.hex}', body={},
                           headers={'Authorization': self.another_token})
        assert result["code"] == 200
        notification = session.query(Notification).filter_by(target_id=self.note.id).one()
        user_notification = session.query(UserNotification).filter_by(user_id=self.user.id).one()
        assert notification
        assert notification.target_id == self.note.id
        assert notification.target_type == 'note'
        assert notification.action == 'watch'
        assert notification.type == 'remind'
        assert notification.sender_id == self.another_user.id
        assert notification.target_desc == self.note.title
        assert user_notification
        assert user_notification.notification_id == notification.id
        assert user_notification.is_read is False

        result = self.get(f'/api/user/notification/', headers={'Authorization': self.token})
        assert result["code"] == 200
        data = result["data"]
        assert data["unread_count"] == 1
        assert len(data["generals"]) == 0
        assert len(data["follows"]) == 0
        assert len(data["stars"]) == 1
        _notification = data["stars"][0]
        assert _notification["is_read"] is False
        assert _notification["target_id"] == self.note.id.hex
        assert _notification["target_type"] == 'note'
        assert _notification["action"] == 'watch'

    @pytest.mark.usefixtures("user", "token", "note", "another_user", "another_token")
    def test_comment_note_notify_owner(self):
        params = {
            "content": "test comment"
        }
        result = self.post(f'/api/note/comment/{self.note.id.hex}', body=params,
                           headers={'Authorization': self.another_token})
        assert result["code"] == 200
        notification = session.query(Notification).filter_by(target_id=self.note.id.hex, action="comment").one()
        user_notification = session.query(UserNotification).filter_by(user_id=self.user.id).one()
        assert notification
        assert notification.target_id.hex == self.note.id.hex
        assert notification.anchor.hex == result["data"]["id"]
        assert notification.target_type == 'note'
        assert notification.action == 'comment'
        assert notification.type == 'remind'
        assert notification.sender_id == self.another_user.id
        assert user_notification
        assert user_notification.notification_id == notification.id
        assert user_notification.is_read is False

        result = self.get(f'/api/user/notification/', headers={'Authorization': self.token})
        assert result["code"] == 200
        data = result["data"]
        assert data["unread_count"] == 1
        assert len(data["generals"]) == 1
        assert len(data["follows"]) == 0
        assert len(data["stars"]) == 0
        _notification = data["generals"][0]
        assert _notification["is_read"] is False
        assert _notification["target_id"] == self.note.id.hex
        assert _notification["target_type"] == 'note'
        assert _notification["target_desc"] == self.note.title
        assert _notification["action"] == 'comment'
        assert _notification["anchor"] == notification.anchor.hex

    @pytest.mark.usefixtures("user", "token", "note", "another_user", "another_token")
    def test_reply_comment_notify_owner(self):
        params = {
            "content": "test comment"
        }
        result = self.post(f'/api/note/comment/{self.note.id.hex}', body=params,
                           headers={'Authorization': self.another_token})
        assert result["code"] == 200
        params = {
            "content": "test comment",
            "reply_to": result["data"]["id"]
        }
        result = self.post(f'/api/note/comment/{self.note.id.hex}', body=params,
                           headers={'Authorization': self.token})
        notification = session.query(Notification).filter_by(target_id=result["data"]["id"], action="reply").one()
        user_notification = session.query(UserNotification).filter_by(user_id=self.another_user.id).one()
        assert notification
        assert notification.target_id.hex == result["data"]["id"]
        assert notification.target_type == 'comment'
        assert notification.action == 'reply'
        assert notification.type == 'remind'
        assert notification.sender_id == self.user.id
        assert user_notification
        assert user_notification.notification_id == notification.id
        assert user_notification.is_read is False

        result = self.get(f'/api/user/notification/', headers={'Authorization': self.another_token})
        assert result["code"] == 200
        data = result["data"]
        assert data["unread_count"] == 1
        assert len(data["generals"]) == 1
        assert len(data["follows"]) == 0
        assert len(data["stars"]) == 0
        _notification = data["generals"][0]
        assert _notification["is_read"] is False
        assert _notification["target_id"] == notification.target_id.hex
        assert _notification["target_type"] == 'comment'
        assert _notification["action"] == 'reply'

    @pytest.mark.usefixtures("user", "token", "note", "another_user", "another_token")
    def test_star_comment_notify_owner(self):
        params = {
            "content": "test comment"
        }
        result = self.post(f'/api/note/comment/{self.note.id.hex}', body=params,
                           headers={'Authorization': self.another_token})
        assert result["code"] == 200
        comment_id = result["data"]["id"]
        result = self.post(f'/api/note/comment/star/{comment_id}',
                           body={},
                           headers={'Authorization': self.token})
        assert result["code"] == 200
        assert result["data"] == 1
        notification = session.query(Notification).filter_by(target_id=self.note.id, target_type="comment", action="star").one()
        user_notification = session.query(UserNotification).filter_by(user_id=self.another_user.id).one()
        assert notification
        assert notification.target_id == self.note.id
        assert notification.target_type == 'comment'
        assert notification.action == 'star'
        assert notification.type == 'remind'
        assert notification.sender_id == self.user.id
        assert user_notification
        assert user_notification.notification_id == notification.id
        assert user_notification.is_read is False

        result = self.get(f'/api/user/notification/', headers={'Authorization': self.another_token})
        assert result["code"] == 200
        data = result["data"]
        assert data["unread_count"] == 1
        assert len(data["generals"]) == 0
        assert len(data["follows"]) == 0
        assert len(data["stars"]) == 1
        _notification = data["stars"][0]
        assert _notification["is_read"] is False
        assert _notification["target_id"] == notification.target_id.hex
        assert _notification["target_type"] == 'comment'
        assert _notification["action"] == 'star'

    @pytest.mark.usefixtures("note", "user", "token", "another_user", "another_token")
    def test_mention_comment_notify(self):
        params = {
            "content": "test comment @another_user",
            "mentions": ["another_user"]
        }
        result = self.post(f'/api/note/comment/{self.note.id.hex}',
                           body=params,
                           headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        comment_id = result["data"]["id"]
        notification = session.query(Notification).filter_by(
            target_id=self.note.id.hex,
            target_type="comment",
            action="at"
        ).one()
        user_notification = session.query(UserNotification).filter_by(user_id=self.another_user.id).one()
        assert notification
        assert notification.target_id.hex == self.note.id.hex
        assert notification.target_type == 'comment'
        assert notification.action == 'at'
        assert notification.type == 'remind'
        assert notification.sender_id == self.user.id
        assert notification.anchor.hex == comment_id
        assert user_notification
        assert user_notification.notification_id == notification.id
        assert user_notification.is_read is False