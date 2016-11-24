# -*- coding: utf-8 -*-

"""
    test_notebook.py
    ~~~~~~~
"""
import pytest
from .base import BaseHTTPTestCase


@pytest.mark.usefixtures("token")
class NotebookTestCase(BaseHTTPTestCase):
    def test_create_notebook_without_token(self):
        data = {
            'name': 'test name',
        }
        result = self.post('/api/notebook/', body=data)
        assert isinstance(result, dict)
        assert result["code"] == 401

    def test_create_notebook(self):
        data = {
            'name': 'test name',
        }
        result = self.post('/api/notebook/', body=data, headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert len(result["data"]["id"]) == 32

    @pytest.mark.usefixtures("notebooks")
    def test_get_notebook(self):
        result = self.get('/api/notebook/', headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert len(result["data"]) == 2
        assert len(result["data"][0]["children"]) == 1
        assert len(result["data"][1]["children"]) == 1
        assert len(result["data"][0]["children"][0]["children"]) == 1
        assert len(result["data"][1]["children"][0]["children"]) == 0

    def test_get_notebook_without_fixture(self):
        result = self.get('/api/notebook/', headers={'Authorization': self.token})
        assert isinstance(result, dict)
        assert result["code"] == 200
        assert len(result["data"]) == 0
