# -*- coding: utf-8 -*-

"""
    base.py
    ~~~~~~~
"""
import json
import logging
from tornado.web import RequestHandler
from note4s.models import Session

class BaseRequestHandler(RequestHandler):

    def __init__(self, *args, **kwargs):
        self.session = Session()
        super().__init__(*args, **kwargs)

    def get_params(self):
        try:
            params = json.loads(self.request.body.decode('utf-8'))
        except Exception as e:
            logging.error(e)
            return {}
        else:
            return params

    def api_fail_response(self, message):
        """
        返回失败的信息
        """
        self.write({
            "code": 400,
            "message": message
        })
        self.session.close()
        self.finish()

    def api_success_response(self, data):
        """
        返回成功的结果
        """
        self.write(json.dumps({
            'code': 200,
            "data": data
        }))
        self.session.close()
        self.finish()
