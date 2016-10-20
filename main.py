# -*- coding: utf-8 -*-

"""
    main.py
    ~~~~~~~
"""
import tornado.web

from note4s.app import app

if __name__ == "__main__":
    app = app(debug=True)
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
