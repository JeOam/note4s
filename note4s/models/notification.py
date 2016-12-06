# -*- coding: utf-8 -*-

"""
    notification.py
    ~~~~~~~
"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean
)
from sqlalchemy.dialects.postgresql import ENUM
from .base import BaseModel

ACTION = ('new note', 'new subnote', 'comment', 'star', 'follow', 'at')
TARGET_TYPE = ('user', 'note', 'subnote', 'notebook')
TYPE = ('remind', 'announce', 'message')
ACTION_ENUM = ENUM(*ACTION, name='action')
TARGET_TYPE_ENUM = ENUM(*TARGET_TYPE, name='target_type')
TYPE_ENUM = ENUM(*TYPE, name='type')

# 参考：http://www.jianshu.com/p/6bf8166b291c

class Notification(BaseModel):
    content = Column(String, nullable=False)
    type = Column(TYPE_ENUM)
    target_id = Column(String(32))
    target_type = Column(TARGET_TYPE_ENUM)
    action = Column(ACTION_ENUM)
    sender_id = Column(String(32))


class UserNotification(BaseModel):
    is_read = Column(Boolean, default=False)
    user_id = Column(String(32))
    notification_id = Column(String(32))


class Subscription(BaseModel):
    target_id = Column(String(32))
    target_type = Column(TARGET_TYPE_ENUM)
    action = Column(ACTION_ENUM)
    user_id = Column(String(32))


class Watch(BaseModel):
    target_id = Column(String(32))
    user_id = Column(String(32))


class Star(BaseModel):
    target_id = Column(String(32))
    user_id = Column(String(32))