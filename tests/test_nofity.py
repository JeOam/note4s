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
    def test_star_note_notify_owner(self):
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
