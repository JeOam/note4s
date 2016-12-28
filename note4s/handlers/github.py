# -*- coding: utf-8 -*-

"""
    github.py
    ~~~~~~~
"""
import logging
import requests
from .base import BaseRequestHandler
from note4s import settings
from note4s.models import User
from note4s.utils import create_jwt


class GithubCallbackHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        code = self.get_argument('code', None)
        if code:
            url = 'https://github.com/login/oauth/access_token'
            result = requests.post(url, data={
                'client_id': settings.GITHUB_ID,
                'client_secret': settings.GITHUB_SECRET,
                'code': code
            }, headers={'Accept': 'application/json'}).json()
            if result.get('access_token'):
                userinfo = requests.get('https://api.github.com/user', headers={
                    'Authorization': f"token {result.get('access_token')}"
                }).json()
                if userinfo.get('login'):
                    username = userinfo.get('login')
                    user = self.session.query(User).filter_by(username=username).first()
                    if user is None:
                        user = User(username=username,
                                    nickname=userinfo.get('name'),
                                    avatar=userinfo.get('avatar_url'),
                                    email=userinfo.get('email'))
                        self.session.add(user)
                        self.session.commit()
                    else:
                        user.nickname = userinfo.get('name')
                        user.avatar = userinfo.get('avatar_url')
                        user.email = userinfo.get('email')
                        self.session.add(user)
                        self.session.commit()
                    return self.redirect(f'http://localhost:8088/redirect?'
                                         f'token={create_jwt(user.id.hex).decode("utf-8")}&'
                                         f'state={self.get_argument("state")}')
        else:
            error = self.get_argument('error')
            error_description = self.get_argument('error_description')
            logging.error(f'Auth Callback Error: {error}: {error_description}')

        return self.redirect('http://localhost:8088/login')
