# -*- coding: utf-8 -*-

"""
    contest.py
    ~~~~~~~
    * Copyright (C) 2016 GridSafe, Inc.
"""
import pytest

from http.cookies import SimpleCookie
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from api.models import Note, CustomUser, NoteBook


@pytest.fixture()
def client(request):
    client = APIClient()
    return client


@pytest.fixture()
def test_user(request):
    user = User(username="test_username",
                email="test@test.com")
    user.set_password("test_password")
    user.save()

    def tear_down():
        user.delete()

    request.addfinalizer(tear_down)
    return user


@pytest.fixture()
def token(client, test_user):
    response = client.post("/api/rest-auth/login/",
                           {
                               'email': "test@test.com",
                               "password": "test_password"
                           },
                           format='json')
    client.cookies = SimpleCookie()
    return response.data["data"]["key"]


@pytest.fixture()
def test_note(request, test_user):
    custom_user = CustomUser.objects.filter(user_id=test_user.id).first()
    note = Note(custom_user=custom_user,
                title="test_title",
                content="test_content")
    note.save()

    def tear_down():
        note.delete()

    request.addfinalizer(tear_down)

    return note


@pytest.fixture()
def test_notebook(request, test_user):
    custom_user = CustomUser.objects.filter(user_id=test_user.id).first()
    notebook = NoteBook(custom_user=custom_user,
                        name="test_notebook_name")
    notebook.save()

    def tear_down():
        notebook.delete()

    request.addfinalizer(tear_down)

    return notebook
