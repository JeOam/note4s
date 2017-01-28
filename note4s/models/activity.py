# -*- coding: utf-8 -*-

"""
    activity.py
    ~~~~~~~
"""
from sqlalchemy import (
    Column,
    String
)
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel
from .notification import ACTION_ENUM, TARGET_TYPE_ENUM


class Activity(BaseModel):
    """
    用户动态：
    谁创建了新的笔记本
    谁在某笔记本写了新的笔记
    谁在某笔记下写了新的子笔记
    谁关注了谁
    谁关注了某笔记本
    谁收藏某笔记本下的某笔记
    """
    user_id = Column(UUID(as_uuid=True))
    action = Column(ACTION_ENUM)
    target_id = Column(UUID(as_uuid=True))
    target_type = Column(TARGET_TYPE_ENUM)
    target_desc = Column(String)
    target_owner_id = Column(UUID(as_uuid=True))
    target_owner_type = Column(TARGET_TYPE_ENUM)
    target_owner_desc = Column(String)
    anchor = Column(UUID(as_uuid=True))
