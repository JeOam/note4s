# -*- coding: utf-8 -*-

"""
    __init__.py
    ~~~~~~~
"""
from .base import engine, Session, BaseModel

from .user import User
from .note import Note
from .notebook import Notebook

# Create all the tables in the database which are
# defined by Base's subclasses such as User
def create_table():
    BaseModel.metadata.create_all()
