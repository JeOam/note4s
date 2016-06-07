# coding=utf-8

from django.db import models
from django.contrib.admin import ModelAdmin, TabularInline

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
    notebook = models.ForeignKey('NoteBook',
                                 db_column='notebook_uuid',
                                 null=True,
                                 related_name='note_sections')
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return str(self.name)


class NoteSectionInline(TabularInline):
    model = NoteSection


class NoteBookAdmin(ModelAdmin):
    inlines = [NoteSectionInline, ]
    list_display = ('uuid', 'custom_user', 'name', 'created_at', 'updated_at')
    list_editable = ('name',)
    search_fields = ('name',)
    ordering = ('updated_at',)


class NoteSectionAdmin(ModelAdmin):
    list_display = ('uuid', 'notebook', 'name', 'created_at', 'updated_at')
    list_editable = ('name',)
    search_fields = ('name',)
    ordering = ('updated_at',)


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
    title = models.CharField(max_length=100)
    content = models.TextField()

    def __str__(self):
        return str(self.title)


class SubNote(BaseModel):
    """
    一个笔记对应多个子笔记
    """
    note = models.ForeignKey('Note',
                             db_column='note_uuid',
                             blank=False,
                             null=False,
                             related_name='sub_notes')
    content = models.TextField()

    def __str__(self):
        return 'SubNote for ' + str(self.note.title)


class SubNoteInline(TabularInline):
    model = SubNote


class NoteAdmin(ModelAdmin):
    inlines = [SubNoteInline, ]
    list_display = ('uuid', 'custom_user', 'note_section', 'title', 'updated_at')
    list_editable = ('title',)
    search_fields = ('title',)
    ordering = ('updated_at',)


class SubNoteAdmin(ModelAdmin):
    list_display = ('uuid', 'note', 'content', 'updated_at')
    list_editable = ('content',)
    search_fields = ('content',)
    ordering = ('updated_at',)
