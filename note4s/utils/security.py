# -*- coding: utf-8 -*-

"""
    encrypt.py
    ~~~~~~~
"""
import jwt
import datetime
import time
from note4s import settings


def create_jwt(user_id):
    timestamp = datetime.datetime.now()
    token = jwt.encode(
        {
            'id': user_id,
            'expire': (datetime.datetime.now() + datetime.timedelta(days=90)).timestamp(),
            'timestamp': timestamp.timestamp()
        },
        settings.JWT_SECRET,
        algorithm='HS256'
    )
    return [timestamp, token]


def extract_jwt(token):
    data = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
    if data.get("expire", 0) >= time.time():
        return [datetime.datetime.fromtimestamp(data.get("timestamp")), data.get("id")]
