# -*- coding: utf-8 -*-

"""
    base.py
    ~~~~~~~
"""
import json

import pytest
from tornado.testing import AsyncHTTPTestCase
from tornado.httputil import url_concat
from note4s.app import app


@pytest.mark.usefixtures("database")
class BaseHTTPTestCase(AsyncHTTPTestCase):
    def get_app(self):
        self.app = app()
        return self.app

    def get(self, url, **kwargs):
        if 'params' in kwargs and isinstance(kwargs['params'], dict):
            url = url_concat(url, kwargs['params'])
            del kwargs['params']

        result = self.fetch(url, method="GET", **kwargs)
        return self.prepare_result(result)

    def post(self, url, **kwargs):
        if 'body' in kwargs and isinstance(kwargs['body'], dict):
            kwargs['body'] = json.dumps(kwargs['body'])

        result = self.fetch(url, method="POST", **kwargs)
        return self.prepare_result(result)

    def delete(self, url, **kwargs):
        result = self.fetch(url, method="DELETE", **kwargs)
        return self.prepare_result(result)

    def prepare_result(self, result):
        try:
            data = json.loads(result.body.decode('utf-8'))
        except:
            if result.body:
                return result.body.decode("utf-8")
            else:
                return result.body
        else:
            return data
