# -*- coding: utf-8 -*-

"""
    organization.py
    ~~~~~~~
"""
from sqlalchemy import (
    Column,
    String
)
from sqlalchemy.dialects.postgresql import UUID, ENUM

from .base import BaseModel

ROLE = ('owner', 'collaborator', 'visitor')
ROLE_ENUM = ENUM(*ROLE, name='role')


class Organization(BaseModel):
    name = Column(String(64), unique=True, nullable=False)
    desc = Column(String(128))
    avatar = Column(String(128))


class Membership(BaseModel):
    organization_id = Column(UUID(as_uuid=True))
    user_id = Column(UUID(as_uuid=True))
    role = Column(ROLE_ENUM)
