# coding=utf-8

import uuid
from django.db import models

__author__ = 'JeOam'


class BaseModel(models.Model):
    class Meta:
        abstract = True

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    updated_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now=True)

    @property
    def uuid_str(self):
        return str(self.uuid).replace("-", "")

    @property
    def created_at_str(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S %Z")
