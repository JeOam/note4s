# -*- coding: utf-8 -*-

"""
    test_api_user.py
    ~~~~~~~
    * Copyright (C) 2016 GridSafe, Inc.
"""
import pytest
from django.contrib.auth.models import User
from api.models import CustomUser


@pytest.mark.usefixtures('client')
def test_registration_failed(client):
    response = client.post("/api/rest-auth/registration/", format='json')
    required = ['This field is required.']
    assert response.status_code == 400
    assert response.data["username"] == required
    assert response.data["email"] == required
    assert response.data["password1"] == required
    assert response.data["password2"] == required


@pytest.mark.django_db
@pytest.mark.usefixtures('client')
def test_registration_success(client):
    response = client.post("/api/rest-auth/registration/",
                           {
                               'username': 'test_username',
                               'email': "test@test.com",
                               "password1": "test_password",
                               "password2": "test_password"},
                           format='json')
    assert response.status_code == 201
    assert response.data.get("key")
    assert len(response.data.get("key")) == 40

    user = User.objects.filter(email="test@test.com").first()
    assert user
    custom_user = CustomUser.objects.filter(user_id=user.id).first()
    assert custom_user


@pytest.mark.django_db
@pytest.mark.usefixtures('client', 'registered')
def test_login_email(client):
    response = client.post("/api/rest-auth/login/",
                           {
                               'email': "test@test.com",
                               "password": "test_password"
                           },
                           format='json')
    assert response.status_code == 200
    assert response.data.get("key")
    assert len(response.data.get("key")) == 40

