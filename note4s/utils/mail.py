# -*- coding: utf-8 -*-

"""
    mail.py
    ~~~~~~~
"""
import requests
from note4s import settings


def sent_mail(from_mail, to_mail, title, content):
    result = requests.post(
        "https://api.mailgun.net/v3/mg.note4s.com/messages",
        auth=("api", settings.MAILGUN_KEY),
        data={"from": from_mail,
              "to": [to_mail],
              "subject": title,
              "html": content}
    )
    return 'id' in result.json()
