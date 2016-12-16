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
    @pytest.mark.usefixtures("user", "note", "another_user", "another_token")
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

    @pytest.mark.usefixtures("user", "note", "another_user", "another_token")
    def test_watch_note_notify_owner(self):
        result = self.post(f'/api/note/watch/{self.note.id.hex}', body={}, headers={'Authorization': self.another_token})
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

    @pytest.mark.usefixtures("user", "note", "another_user", "another_token")
    def test_comment_note_notify_owner(self):
        params = {
            "content": "test comment"
        }
        result = self.post(f'/api/note/comment/{self.note.id.hex}', body=params,
                           headers={'Authorization': self.another_token})
        assert result["code"] == 200
        notification = session.query(Notification).filter_by(target_id=result["data"]["id"], action="comment").one()
        user_notification = session.query(UserNotification).filter_by(user_id=self.user.id).one()
        assert notification
        assert notification.target_id.hex == result["data"]["id"]
        assert notification.target_type == 'comment'
        assert notification.action == 'comment'
        assert notification.type == 'remind'
        assert notification.sender_id == self.another_user.id
        assert user_notification
        assert user_notification.notification_id == notification.id
        assert user_notification.is_read is False

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
        notification = session.query(Notification).filter_by(target_id=comment_id, action="star").one()
        user_notification = session.query(UserNotification).filter_by(user_id=self.another_user.id).one()
        assert notification
        assert notification.target_id.hex == comment_id
        assert notification.target_type == 'comment'
        assert notification.action == 'star'
        assert notification.type == 'remind'
        assert notification.sender_id == self.user.id
        assert user_notification
        assert user_notification.notification_id == notification.id
        assert user_notification.is_read is False