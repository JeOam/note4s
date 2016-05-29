# -*- coding: utf-8 -*-

"""
    contest.py
    ~~~~~~~
    * Copyright (C) 2016 GridSafe, Inc.
"""
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
