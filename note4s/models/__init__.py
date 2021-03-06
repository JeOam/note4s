# -*- coding: utf-8 -*-

"""
    __init__.py
    ~~~~~~~
"""
from .base import engine, Session, BaseModel

from .user import User
from .note import Note
from .notebook import Notebook, OWNER_TYPE
from .notification import (
    Notification,
    ACTION as N_ACTION,
    TYPE as N_TYPE,
    TARGET_TYPE as N_TARGET_TYPE,
    UserNotification,
    Watch,
    Star
)
from .activity import Activity
from .comment import Comment
from .organization import (
    Organization,
    Membership,
    ROLE as O_ROLE
)

# Create all the tables in the database which are
# defined by Base's subclasses such as User
def create_table():
    BaseModel.metadata.create_all(engine)

def drop_table():
    BaseModel.metadata.drop_all(engine)