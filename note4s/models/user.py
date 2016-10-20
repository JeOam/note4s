# -*- coding: utf-8 -*-

"""
    user.py
    ~~~~~~~
"""
from sqlalchemy import (
    Column,
    String
)

from .base import BaseModel


class User(BaseModel):
    username = Column(String(64), unique=True, nullable=False)
    nickname = Column(String(64))
    email = Column(String(64), unique=True)
    password = Column(String(128))
    avatar = Column(String(128))
