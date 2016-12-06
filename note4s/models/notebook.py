# -*- coding: utf-8 -*-

"""
    notebook.py
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


class Notebook(BaseModel):
    name = Column(String(64))
    parent_id = Column(UUID(as_uuid=True))
    note_id = Column(UUID(as_uuid=True))
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    user = relationship(User, backref=backref("notebooks", cascade="all, delete-orphan"))
