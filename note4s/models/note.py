# -*- coding: utf-8 -*-

"""
    note.py
    ~~~~~~~
"""
from sqlalchemy import (
    Column,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship, backref

from .base import BaseModel
from .user import User


class Note(BaseModel):
    title = Column(String(128), nullable=False)
    content = Column(String)
    parent_id = Column(String(64))
    user_id = Column(String, ForeignKey('user.id'))
    user = relationship(User, backref=backref("notes", cascade="all, delete-orphan"))
