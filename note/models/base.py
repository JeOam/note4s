# coding=utf-8

from django.db import models

__author__ = 'JeOam'


class BaseModel(models.Model):
    class Meta:
        abstract = True

    uuid = models.UUIDField(primary_key=True)
    updated_at = models.DateTimeField()
    created_at = models.DateTimeField()
