# -*- coding: utf-8 -*-

"""
    timeline.py
    ~~~~~~~
"""
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean
)
from .base import BaseModel

class Activity(BaseModel):
    user_id = Column(String(32))
    content = Column(String, nullable=False)
    index = Column(Integer)
    reply_to = Column(String(32))
    star = Column(Integer)
    is_valid = Column(Boolean)