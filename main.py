# -*- coding: utf-8 -*-

"""
    main.py
    ~~~~~~~
"""
import logging.config
from datetime import datetime
import tornado
from tornado import autoreload
from note4s.app import app
from note4s import settings


def reload_hook():
    print(f'''

    ******************
    Server Reload at {datetime.now()}
    ******************

    ''')


if __name__ == "__main__":
    logging.config.dictConfig(settings.LOGGING)
    autoreload._reload_hooks.append(reload_hook)
    app = app(debug=True)
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
