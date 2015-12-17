# coding=utf-8

from django.db import models
from django.contrib.auth.models import User

from .base import BaseModel

__author__ = 'JeOam'

class CustomUser(BaseModel):
    """
    自定义的 User 表
    """
    user = models.OneToOneField(User, blank=True, null=True)
    nickname = models.CharField(max_length=50)
    avatar = models.CharField(max_length=200)

    def __str__(self):
        return str(self.user.nickname)
