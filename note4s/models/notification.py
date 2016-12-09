# -*- coding: utf-8 -*-

"""
    notification.py
    ~~~~~~~
"""

from sqlalchemy import (
    Column,
    String,
    Boolean
)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from .base import BaseModel

ACTION = ('new note', 'new subnote', 'comment', 'star', 'watch', 'at')
TARGET_TYPE = ('user', 'note', 'subnote', 'notebook')
TYPE = ('remind', 'announce', 'message')
ACTION_ENUM = ENUM(*ACTION, name='action')
TARGET_TYPE_ENUM = ENUM(*TARGET_TYPE, name='target_type')
TYPE_ENUM = ENUM(*TYPE, name='type')

class Notification(BaseModel):
    type = Column(TYPE_ENUM)
    target_id = Column(UUID(as_uuid=True))
    target_type = Column(TARGET_TYPE_ENUM)
    target_desc = Column(String)
    action = Column(ACTION_ENUM)
    sender_id = Column(UUID(as_uuid=True))


class UserNotification(BaseModel):
    is_read = Column(Boolean, default=False)
    user_id = Column(UUID(as_uuid=True))
    notification_id = Column(UUID(as_uuid=True))


class Subscription(BaseModel):
    target_id = Column(UUID(as_uuid=True))
    target_type = Column(TARGET_TYPE_ENUM)
    action = Column(ACTION_ENUM)
    user_id = Column(UUID(as_uuid=True))


class Watch(BaseModel):
    target_id = Column(UUID(as_uuid=True))
    target_type = Column(TARGET_TYPE_ENUM)
    user_id = Column(UUID(as_uuid=True))


class Star(BaseModel):
    target_id = Column(UUID(as_uuid=True))
    target_type = Column(TARGET_TYPE_ENUM)
    user_id = Column(UUID(as_uuid=True))