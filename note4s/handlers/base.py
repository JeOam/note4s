# -*- coding: utf-8 -*-

"""
    base.py
    ~~~~~~~
"""
import json
import logging
from tornado.web import RequestHandler
from sqlalchemy import exc
from note4s.models import Session, User
from note4s.utils import extract_jwt


class BaseRequestHandler(RequestHandler):
    def __init__(self, *args, **kwargs):
        self.session = Session()
        super().__init__(*args, **kwargs)

    def get_current_user(self):
        token = self.request.headers.get("Authorization")
        if token:
            user_id = extract_jwt(token)
            if user_id:
                try:
                    user = self.session.query(User).filter_by(id=user_id).one()
                except exc.NoResultFound:
                    logging.error('No user with id {}'.format(user_id))
                else:
                    return user

    def prepare(self):
        if self.request.path.startswith("/api/"):
            if not self.current_user:
                self.api_fail_response("Authorization Required.", 401)

    def get_params(self):
        try:
            params = json.loads(self.request.body.decode('utf-8'))
        except Exception as e:
            logging.error(e)
            return {}
        else:
            return params

    def options(self, *args, **kwargs):
        self.set_header('Access-Control-Allow-Origin', 'http://localhost:8088')
        self.set_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.finish()

    def api_fail_response(self, message, code=400):
        """
        返回失败的信息
        """
        self.write({
            "code": code,
            "message": message
        })
        self.set_header('Access-Control-Allow-Origin', 'http://localhost:8088')
        self.set_header('Content-Type', 'application/json')
        self.finish()

    def api_success_response(self, data, code=200):
        """
        返回成功的结果
        """
        self.write(json.dumps({
            'code': code,
            "data": data
        }))
        self.set_header('Access-Control-Allow-Origin', 'http://localhost:8088')
        self.set_header('Content-Type', 'application/json')
        self.finish()

    def on_finish(self):
        self.session.close()