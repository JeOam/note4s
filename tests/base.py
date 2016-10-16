# -*- coding: utf-8 -*-

"""
    base.py
    ~~~~~~~
"""
import json

import pytest
from tornado.testing import AsyncHTTPTestCase

from note4s.app import app

@pytest.mark.usefixtures("database")
class BaseHTTPTestCase(AsyncHTTPTestCase):
    def get_app(self):
        self.app = app()
        return self.app

    def get(self, url, **kwargs):
        return self.fetch(url, headers={}, **kwargs)

    def post(self, url, **kwargs):
        if 'body' in kwargs and isinstance(kwargs['body'], dict):
            kwargs['body'] = json.dumps(kwargs['body'])

        result = self.fetch(url, method="POST", **kwargs)

        try:
            data = json.loads(result.body.decode('utf-8'))
        except:
            return result.body.decode("utf-8")
        else:
            return data
