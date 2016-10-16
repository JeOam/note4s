# -*- coding: utf-8 -*-

"""
    note.py
    ~~~~~~~
"""
from sqlalchemy import (
    Column,
    String
)

from .base import BaseModel

class Note(BaseModel):
    title = Column(String(128), nullable=False)
    content = Column(String)
    parent_id = Column(String(64))
