# coding=utf-8

from django.db import models

from .base import BaseModel

__author__ = 'JeOam'


class NoteBook(BaseModel):
    """
    笔记分类的最大类别
    """
    custom_user = models.ForeignKey('CustomUser',
                                    db_column='custom_user_uuid',
                                    null=True,
                                    related_name='notebooks')
    name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.name)


class NoteSection(BaseModel):
    """
    把一些笔记归类在 章/模块 单位上；
    分类级别比 NoteBook 小一个层级
    """
    note_book = models.ForeignKey('NoteBook',
                                  db_column='note_book_uuid',
                                  null=True,
                                  related_name='note_sections')
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return str(self.name)


class Note(BaseModel):
    """
    一个笔记，站内内容的的核心组成元素
    """
    custom_user = models.ForeignKey('CustomUser',
                                    db_column='custom_user_uuid',
                                    null=True)
    note_section = models.ForeignKey('NoteSection',
                                     db_column='note_section_uuid',
                                     null=True,
                                     related_name='notes')
    title = models.CharField(max_length=100, unique=True)
    content = models.TextField()

    def __str__(self):
        return str(self.title)


class SubNote(BaseModel):
    """
    一个笔记对应多个子笔记
    """
    note = models.ForeignKey('Note',
                             db_column='note_uuid',
                             null=True,
                             related_name='sub_notes')
    content = models.TextField()

    def __str__(self):
        return 'SubNote for ' + str(self.note.title)
