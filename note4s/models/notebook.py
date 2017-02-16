# -*- coding: utf-8 -*-

"""
    notebook.py
    ~~~~~~~
"""
from sqlalchemy import (
    Column,
    String
)
from sqlalchemy.dialects.postgresql import UUID, ENUM

from .base import BaseModel

OWNER_TYPE = ('user', 'organization')
OWNER_TYPE_ENUM = ENUM(*OWNER_TYPE, name='owner_type')


class Notebook(BaseModel):
    name = Column(String(64))
    parent_id = Column(UUID(as_uuid=True))
    note_id = Column(UUID(as_uuid=True))
    owner_id = Column(UUID(as_uuid=True))
    owner_type = Column(OWNER_TYPE_ENUM)