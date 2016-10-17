# -*- coding: utf-8 -*-

"""
    conftest.py
    ~~~~~~~
"""
import pytest
from werkzeug.security import generate_password_hash
from note4s.models import engine, BaseModel, Session, \
    User
from note4s.utils import create_jwt


@pytest.fixture(scope="function")
def database(request):
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)

    def finalizer():
        BaseModel.metadata.drop_all(engine)
    request.addfinalizer(finalizer)
    return engine


@pytest.fixture(scope="function")
def user(database, request):
    session = Session()
    user = User(username="test",
                email="test@test.com",
                password=generate_password_hash("123456"))
    session.add(user)
    session.commit()

    def finalizer():
        session.delete(user)
        session.commit()
    request.addfinalizer(finalizer)
    return user


@pytest.fixture(scope="function")
def token(user, request):
    token = create_jwt(user_id=user.id).decode("utf-8")
    request.cls.token = token
    return token
