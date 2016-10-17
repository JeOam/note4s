# -*- coding: utf-8 -*-

"""
    test_login.py
    ~~~~~~~
"""
import pytest
from .base import BaseHTTPTestCase

class UserTestCase(BaseHTTPTestCase):

    @pytest.mark.usefixtures("user")
    def test_login(self):
        data = {
            'email': 'test@test.com',
            'password': '123456'
        }
        result = self.post('/auth/login/', body=data)
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert len(result["data"]) >= 171

    def test_register(self):
        data = {
            'username': 'test',
            'email': 'test@test.com',
            'password': 'admin123'
        }
        result = self.post('/auth/register/', body=data)
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert result["data"]["id"]
        assert result["data"]["email"] == data["email"]
        assert not result["data"].get("password")
