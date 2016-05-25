# coding=utf-8

from django.contrib import admin
from django.db.models.base import ModelBase
from api import models

__author__ = 'JeOam'

model_list = []
for m in dir(models):
    attr = getattr(models, m)
    if isinstance(attr, ModelBase):
        model_list.append(attr)

for model in model_list:
    admin.site.register(model)
