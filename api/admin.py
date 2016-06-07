# coding=utf-8

from django.contrib import admin
from django.db.models.base import ModelBase
from api import models

__author__ = 'JeOam'

_model_dict = {}
_attribute_names = dir(models)
for model_name in _attribute_names:
    model = getattr(models, model_name)
    if isinstance(model, ModelBase):
        admin_model_name = model_name + "Admin"
        if admin_model_name in _attribute_names:
            _model_dict[model] = getattr(models, admin_model_name)
        else:
            _model_dict[model] = None

for model, admin_model in _model_dict.items():
    admin.site.register(model, admin_class=admin_model)
