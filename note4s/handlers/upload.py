# -*- coding: utf-8 -*-

"""
    upload.py
    ~~~~~~~
"""
import uuid
import os
from .base import BaseRequestHandler
from note4s import settings

class UploadHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        file = self.request.files['file'][0]
        fname = file['filename']
        extn = os.path.splitext(fname)[1]
        cname = str(uuid.uuid4().hex) + extn
        fh = open(settings.FILE_FOLDER + cname, 'wb')
        fh.write(file['body'])
        self.api_success_response(cname)

class FileHandler(BaseRequestHandler):
    def get(self, filename):
        with open(settings.FILE_FOLDER + filename, 'rb') as f:
            data = f.read()
            self.write(data)
        self.finish()
