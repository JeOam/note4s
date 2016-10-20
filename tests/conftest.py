# -*- coding: utf-8 -*-

"""
    conftest.py
    ~~~~~~~
"""
import pytest
from werkzeug.security import generate_password_hash
from note4s.models import engine, BaseModel, Session, \
    User, Note, Notebook
from note4s.utils import create_jwt

session = Session()


@pytest.fixture(scope="function")
def database(request):
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)

    def finalizer():
        session.close()
        BaseModel.metadata.drop_all(engine)

    request.addfinalizer(finalizer)
    return engine


@pytest.fixture(scope="function")
def user(database, request):
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


@pytest.fixture(scope="function")
def note(user, request):
    note = Note(user=user,
                title="test title",
                content="test content")
    session.add(note)
    session.commit()

    def finalizer():
        session.delete(note)
        session.commit()

    request.addfinalizer(finalizer)
    request.cls.note = note
    return note


@pytest.fixture(scope="function")
def notebooks(user, request):
    note = Note(user=user,
                title="test title",
                content="test content")
    notebook1 = Notebook(user=user,
                         name="test notebook1")
    notebook2 = Notebook(user=user,
                         name="test notebook2")
    session.add(notebook1)
    session.add(notebook2)
    session.commit()
    note_section1 = Notebook(user=user,
                             name="test note section 1",
                             parent_id=notebook1.id)
    note_section2 = Notebook(user=user,
                             name="test note section 2",
                             parent_id=notebook2.id)
    session.add(note_section1)
    session.add(note_section2)
    session.commit()
    notebook_note = Notebook(user=user,
                             name=note.title,
                             note_id=note.id,
                             parent_id=note_section1.id)
    session.add(notebook_note)
    session.commit()

    def finalizer():
        session.delete(notebook1)
        session.delete(notebook2)
        session.delete(note_section1)
        session.delete(note_section2)
        session.delete(notebook_note)
        session.commit()

    request.addfinalizer(finalizer)
