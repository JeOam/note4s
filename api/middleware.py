# -*- coding: utf-8 -*-

"""
    middleware.py
    ~~~~~~~
    * Copyright (C) 2016 GridSafe, Inc.
"""
from django.http import JsonResponse

class APIMiddleware(object):
    def process_response(self, request, response):
        if request.path.startswith("/api"):
            if response.status_code >= 400:
                data = {
                    "code": 400,
                    "message": response.data,
                    "data": []
                }
                custom_response = JsonResponse(data=data, status=200)
                self.config_CORS(custom_response)
                return custom_response

            elif 200 <= response.status_code < 300:
                data = {
                    "code": 200,
                    "message": '',
                    "data": response.data
                }
                custom_response = JsonResponse(data=data, status=200)
                self.config_CORS(custom_response)
                return custom_response
        else:
            self.config_CORS(response)
            return response

    def config_CORS(self, response):
        response["Access-Control-Allow-Origin"] = "http://127.0.0.1:8080"
        response["Access-Control-Allow-Headers"] = "content-type, authorization"
