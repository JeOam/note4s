# coding=utf-8

from django.db import models
from django.contrib.auth.models import AbstractUser

from .base import BaseModel

__author__ = 'JeOam'


class User(AbstractUser):
    '''
    django.contrib.auth.models.User 默认 User 类字段太少
    用 AbstractUser 自定义一个 User 类，增加字段
    '''
    nickname = models.CharField(max_length=50)
    avatar = models.CharField(max_length=200)


class Note(BaseModel):
    '''
    一个笔记，站内内容的的核心组成元素
    '''
    title = models.CharField(max_length=100)
    content = models.TextField()
