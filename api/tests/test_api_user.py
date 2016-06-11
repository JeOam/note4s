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
    assert response.status_code == 200
    assert response.data["status"] == "FAILURE"
    assert response.data["message"] == '注册出错'


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
    assert response.status_code == 200
    assert response.data["status"] == "SUCCESS"
    assert len(response.data["data"].get("key")) == 40

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
    assert response.data["status"] == "SUCCESS"
    assert len(response.data["data"]["key"]) == 40
