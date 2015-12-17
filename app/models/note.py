# coding=utf-8

from django.db import models

from .base import BaseModel

__author__ = 'JeOam'

class Note(BaseModel):
    """
    一个笔记，站内内容的的核心组成元素
    """
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return str(self.title)


class SubNote(BaseModel):
    """
    一个笔记对应多个子笔记
    """
    note = models.ForeignKey('Note',
                             db_column='note_uuid')
    content = models.TextField()

    def __str__(self):
        return 'SubNote for ' + str(self.note.title)
