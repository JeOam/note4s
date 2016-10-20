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

from .base import BaseModel
from .user import User


class Notebook(BaseModel):
    name = Column(String(64))
    parent_id = Column(String(32))
    note_id = Column(String(32))
    user_id = Column(String, ForeignKey('user.id'))
    user = relationship(User, backref=backref("notebooks", cascade="all, delete-orphan"))
