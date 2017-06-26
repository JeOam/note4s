# -*- coding: utf-8 -*-

"""
    base.py
    ~~~~~~~
"""
import json
import logging
from tornado.web import RequestHandler
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
                user = self.session.query(User).filter_by(id=user_id).one_or_none()
                if user:
                    return user
                else:
                    logging.error(f'No user with id {user_id}')

    def prepare(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.set_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.set_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
        self.set_header('Access-Control-Expose-Headers', 'Content-Type, Content-Disposition')
        if self.request.path.startswith("/api/") and \
           self.request.method != 'GET' and \
           self.request.method != 'OPTIONS':
            if not self.current_user:
                self.api_fail_response("Authorization Required.", 401)

    def options(self, *args, **kwargs):
        self.write({
            "code": 200,
            "message": 'success'
        })
        self.finish()

    def get_params(self):
        """
        for Method POST
        """
        try:
            params = json.loads(self.request.body.decode('utf-8'))
        except Exception as e:
            logging.error(e)
            return {}
        else:
            return params

    def update_modal(self, modal, keys):
        params = self.get_params()
        for column in modal.__table__.columns:
            if column.name in keys:
                data = params.get(column.name, getattr(modal, column.name))
                setattr(modal, column.name, data)

    def api_fail_response(self, message, code=400):
        """
        返回失败的信息
        """
        self.write({
            "code": code,
            "message": message
        })
        self.finish()

    def api_success_response(self, data, code=200):
        """
        返回成功的结果
        """
        self.write({
            'code': code,
            "data": data
        })
        self.finish()

    def write_error(self, status_code, **kwargs):
        if self.__class__ == BaseRequestHandler:
            if 400 <= status_code < 500:
                self.set_status(200)
                self.write({
                    'code': status_code,
                    "data": 'Invalid Request'
                })
                self.finish()
            elif status_code >= 500:
                self.set_status(200)
                self.write({
                    'code': status_code,
                    "data": 'Something went wrong,we will Fix it soon,you may please try again'
                })
                self.finish()
        else:
            if self.settings.get("serve_traceback") and "exc_info" in kwargs:
                # in debug mode, print traceback message
                logging.error(*kwargs["exc_info"])
            super().write_error(status_code, **kwargs)

    def on_finish(self):
        self.session.close()
