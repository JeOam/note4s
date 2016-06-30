# -*- coding: utf-8 -*-

"""
    middleware.py
    ~~~~~~~
    * Copyright (C) 2016 GridSafe, Inc.
"""
import json
from rest_framework.response import Response

SUCCESS = "SUCCESS"
FAILURE = "FAILURE"


class APIMiddleware(object):
    def process_response(self, request, response):
        if request.path.startswith("/api"):
            if response.status_code >= 400:
                if request.path == "/api/rest-auth/registration/":
                    message = "注册出错"
                elif request.path == "/api/rest-auth/login/":
                    message = "登录出错"
                elif request.path == "/api/note/":
                    message = "笔记出错"
                elif request.path == "/api/sub_note/":
                    message = "子笔记出错"
                elif request.path == "/api/notebook/":
                    message = "笔记本出错"
                else:
                    return response

                data = {
                    "status": FAILURE,
                    "message": message,
                    "detail": response.data
                }
                custom_response = Response(data=data, status=200)
                custom_response.content = json.dumps(data).encode('utf-8')
                self.config_CORS(custom_response)
                return custom_response

            elif 200 <= response.status_code < 300:
                data = {
                    "status": SUCCESS,
                    "data": response.data
                }
                custom_response = Response(data=data, status=200)
                custom_response.content = json.dumps(data).encode('utf-8')
                self.config_CORS(custom_response)
                return custom_response
        else:
            self.config_CORS(response)
            return response

    def config_CORS(self, response):
        response["Access-Control-Allow-Origin"] = "http://localhost:8080"
        response["Access-Control-Allow-Headers"] = "content-type"
