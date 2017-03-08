# -*- coding: utf-8 -*-

"""
    note.py
    ~~~~~~~
"""
from sqlalchemy import (
    Column,
    String,
    ForeignKey
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel
from .user import User


class Note(BaseModel):
    title = Column(String(128))
    content = Column(String)
    parent_id = Column(UUID(as_uuid=True))
    section_id = Column(UUID(as_uuid=True))
    notebook_id = Column(UUID(as_uuid=True))
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    user = relationship(User, backref=backref("notes", cascade="all, delete-orphan"))
