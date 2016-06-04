# -*- coding: utf-8 -*-

"""
    contest.py
    ~~~~~~~
    * Copyright (C) 2016 GridSafe, Inc.
"""
from http.cookies import SimpleCookie
import pytest
from rest_framework.test import APIClient


@pytest.fixture()
def client(request):
    client = APIClient()
    return client


@pytest.fixture()
def registered(client):
    client.post("/api/rest-auth/registration/",
                {
                    'username': 'test_username',
                    'email': "test@test.com",
                    "password1": "test_password",
                    "password2": "test_password"
                },
                format='json')


@pytest.fixture()
def token(client):
    response = client.post("/api/rest-auth/registration/",
                           {
                               'username': 'test_username',
                               'email': "test@test.com",
                               "password1": "test_password",
                               "password2": "test_password"
                           },
                           format='json')
    client.cookies = SimpleCookie()
    return response.data["key"]


@pytest.fixture()
def test_note(client, token):
    response = client.post("/api/note/",
                           {
                               "title": "test_title",
                               "content": "test_content",
                           },
                           format='json',
                           HTTP_AUTHORIZATION='Token {}'.format(token))
    return response.data


@pytest.fixture()
def test_notebook(client, token):
    response = client.post("/api/notebook/",
                           {
                               "name": "test_notebook_name"
                           },
                           format='json',
                           HTTP_AUTHORIZATION='Token {}'.format(token))
    return response.data