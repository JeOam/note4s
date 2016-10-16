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
    DateTime,
    String
)
from sqlalchemy.ext.declarative import declarative_base, declared_attr

from sqlalchemy.orm import sessionmaker
from note4s import settings
from note4s.utils import underscore_naming

engine = create_engine(settings.PG_URL, pool_recycle=3600, pool_size=20)
Session = sessionmaker(bind=engine)

class Base:
    @declared_attr
    def __tablename__(cls):
        return underscore_naming(cls.__name__)

    id = Column(String(36), default=lambda: uuid.uuid4().hex, primary_key=True, index=True)
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        result = {}
        exclude = set(["password", "parent_id"])
        for column in self.__table__.columns:
            if column.name in exclude:
                continue

            if isinstance(getattr(self, column.name), datetime):
                result[column.name] = str(getattr(self, column.name))
            else:
                result[column.name] = getattr(self, column.name)
        return result

BaseModel = declarative_base(cls=Base)
