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
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from .base import BaseModel

class Comment(BaseModel):
    note_id = Column(UUID(as_uuid=True))
    user_id = Column(UUID(as_uuid=True))
    content = Column(String, nullable=False)
    index = Column(Integer)
    reply_to = Column(UUID(as_uuid=True))
    star_ids = Column(ARRAY(UUID(as_uuid=True), dimensions=1), default=[])
    is_valid = Column(Boolean, default=True)
