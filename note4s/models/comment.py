# -*- coding: utf-8 -*-

"""
    comment.py
    ~~~~~~~
"""
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean
)
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel

class Comment(BaseModel):
    note_id = Column(UUID(as_uuid=True))
    user_id = Column(UUID(as_uuid=True))
    content = Column(String, nullable=False)
    index = Column(Integer)
    reply_to = Column(UUID(as_uuid=True))
    star = Column(Integer, default=0)
    is_valid = Column(Boolean, default=True)
