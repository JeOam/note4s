# coding=utf-8

from django.db import models, transaction
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .base import BaseModel

__author__ = 'JeOam'


class CustomUser(BaseModel):
    """
    自定义的 User 表
    """
    user = models.OneToOneField(User, blank=True, null=True, related_name='CustomUser')
    avatar = models.CharField(max_length=200)

    def __str__(self):
        return str(self.user.username)


class CustomUserAdmin(ModelAdmin):
    list_display = ('uuid', 'user', 'avatar', 'created_at', 'updated_at')
    ordering = ('updated_at',)


@receiver(post_save, sender=User)
@transaction.atomic
def custom_user_creator(sender, instance, **kwargs):
    if kwargs['created']:
        CustomUser.objects.create(user=instance)
