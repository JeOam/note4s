# -*- coding: utf-8 -*-

"""
    notebook.py
    ~~~~~~~
"""
from sqlalchemy import (
    Column,
    String
)

from .base import BaseModel

class Notebook(BaseModel):
    name = Column(String(64))
    parent_id = Column(String(32))