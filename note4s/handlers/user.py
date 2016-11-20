# -*- coding: utf-8 -*-

"""
    user.py
    ~~~~~~~
"""
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import exc
from note4s.models import User
from note4s.utils import create_jwt
from .base import BaseRequestHandler


class LoginHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        email = params.get("email", None)
        password = params.get("password", None)
        if (not email) or (not password):
            self.api_fail_response("Not Enough Fields")
            return
        try:
            user = self.session.query(User).filter_by(email=email).one()
        except (exc.NoResultFound, exc.MultipleResultsFound) as e:
            self.api_fail_response('Login Failed. Please check you account and password.')
            return
        else:
            self.api_success_response(create_jwt(user.id).decode("utf-8"))


class RegisterHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        username = params.get("username", None)
        email = params.get("email", None)
        password = params.get("password", None)
        if (not email) or (not password) or (not username):
            self.api_fail_response("Not Enough Fields")
            return

        user = User(username=username,
                    email=email,
                    password=generate_password_hash(password))
        try:
            self.session.add(user)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            self.api_fail_response("Failed to create user.")
        else:
            self.api_success_response(user.to_dict())

class CheckHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        username = params.get("username", None)
        user = self.session.query(User).filter_by(username=username).all()
        if len(user) == 0:
            self.api_success_response(True)
        else:
            self.api_fail_response(False)


class ProfileHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        user = self.current_user
        self.api_success_response(user.to_dict())