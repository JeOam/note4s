# -*- coding: utf-8 -*-

"""
    base.py
    ~~~~~~~
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    DateTime
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.declarative.base import _declarative_constructor

from sqlalchemy.orm import sessionmaker
from note4s import settings
from note4s.utils import underscore_naming

engine = create_engine(settings.PG_URL, pool_recycle=3600, pool_size=20)
Session = sessionmaker(bind=engine)


class Base:
    @declared_attr
    def __tablename__(cls):
        return underscore_naming(cls.__name__)

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, **kwargs):
        self.id = uuid.uuid4()
        _declarative_constructor(self, **kwargs)

    def to_dict(self, columns=[]):
        result = {}
        exclude = set(["password", "parent_id"])
        for column in self.__table__.columns:
            if column.name in exclude:
                continue
            if len(columns) and column.name not in columns:
                continue
            if isinstance(getattr(self, column.name), datetime):
                result[column.name] = str(getattr(self, column.name))
            elif isinstance(getattr(self, column.name), uuid.UUID):
                result[column.name] = getattr(self, column.name).hex
            else:
                result[column.name] = getattr(self, column.name)
        return result


BaseModel = declarative_base(cls=Base, constructor=Base.__init__)
