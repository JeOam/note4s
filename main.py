# -*- coding: utf-8 -*-

"""
    main.py
    ~~~~~~~
"""
import logging.config
import tornado.web

from note4s.app import app
from note4s import settings

if __name__ == "__main__":
    logging.config.dictConfig(settings.LOGGING)
    app = app(debug=True)
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
