# -*- coding: utf-8 -*-

"""
    conftest.py
    ~~~~~~~
"""
import shutil
import pytest
from werkzeug.security import generate_password_hash
from note4s.models import engine, BaseModel, Session, \
    User, Note, Notebook, OWNER_TYPE
from note4s.utils import create_jwt
from note4s import settings

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
    user = User(username="test_user",
                email="test@test.com",
                password=generate_password_hash("123456"),
                avatar="http://placehold.it/128x128")
    session.add(user)
    session.commit()

    def finalizer():
        shutil.rmtree(settings.GIT_DIR + user.id.hex, ignore_errors=True)
        session.delete(user)
        session.commit()

    request.addfinalizer(finalizer)
    request.cls.user = user
    return user

@pytest.fixture(scope="function")
def another_user(database, request):
    user = User(username="another_user",
                email="test@test.cn",
                password=generate_password_hash("123456"),
                avatar="http://placehold.it/128x128")
    session.add(user)
    session.commit()

    def finalizer():
        shutil.rmtree(settings.GIT_DIR + user.id.hex, ignore_errors=True)
        session.delete(user)
        session.commit()

    request.addfinalizer(finalizer)
    request.cls.another_user = user
    return user

@pytest.fixture(scope="function")
def token(user, request):
    token = create_jwt(user_id=user.id.hex).decode("utf-8")
    request.cls.token = token
    return token

@pytest.fixture(scope="function")
def another_token(another_user, request):
    token = create_jwt(user_id=another_user.id.hex).decode("utf-8")
    request.cls.another_token = token
    return token

@pytest.fixture(scope="function")
def note_section(user, request):
    notebook = Notebook(owner_id=user.id,
                        owner_type=OWNER_TYPE[0],
                        name="test notebook")
    note_section = Notebook(owner_id=user.id,
                            owner_type=OWNER_TYPE[0],
                            name="test note section",
                            parent_id=notebook.id)
    session.add(notebook)
    session.add(note_section)
    session.commit()
    def finalizer():
        session.delete(notebook)
        session.delete(note_section)
        session.commit()

    request.addfinalizer(finalizer)
    request.cls.note_section = note_section
    return note_section

@pytest.fixture(scope="function")
def note(user, note_section, request):
    note = Note(user=user,
                title="test title",
                content="test content",
                section_id=note_section.id,
                notebook_id=note_section.parent_id)
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
    notebook1 = Notebook(owner_id=user.id,
                         owner_type=OWNER_TYPE[0],
                         name="test notebook1")
    notebook2 = Notebook(owner_id=user.id,
                         owner_type=OWNER_TYPE[0],
                         name="test notebook2")
    note_section1 = Notebook(owner_id=user.id,
                             owner_type=OWNER_TYPE[0],
                             name="test note section 1",
                             parent_id=notebook1.id)
    note_section2 = Notebook(owner_id=user.id,
                             owner_type=OWNER_TYPE[0],
                             name="test note section 2",
                             parent_id=notebook2.id)
    notebook_note = Notebook(owner_id=user.id,
                             owner_type=OWNER_TYPE[0],
                             name=note.title,
                             note_id=note.id,
                             parent_id=note_section1.id)
    note.notebook_id = notebook1.id
    note.section_id = note_section1.id
    session.add(notebook1)
    session.add(notebook2)
    session.add(note_section1)
    session.add(note_section2)
    session.add(note)
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
