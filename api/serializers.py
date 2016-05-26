# -*- coding: utf-8 -*-

"""
    serializers.py
    ~~~~~~~
    * Copyright (C) 2016 GridSafe, Inc.
"""
from rest_framework import serializers
from .models import CustomUser, Note, SubNote, NoteBook, NoteSection


class PureNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('uuid_str', 'title', 'created_at', 'updated_at')


class NoteSectionSerializer(serializers.ModelSerializer):
    notes = PureNoteSerializer(many=True, read_only=True)

    class Meta:
        model = NoteSection
        fields = ('uuid_str', 'name', 'notes')


class NoteBookSerializer(serializers.ModelSerializer):
    note_sections = NoteSectionSerializer(many=True, read_only=True)

    class Meta:
        model = NoteBook
        fields = ('uuid_str', 'name', 'note_sections')


class UserSerializer(serializers.ModelSerializer):
    notebooks = NoteBookSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ('uuid_str', 'nickname', 'avatar', 'notebooks')

class SubNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubNote
        fields = ('uuid_str', 'content', 'created_at', 'updated_at')

class NoteSerializer(serializers.ModelSerializer):
    sub_notes = SubNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = ('uuid_str', 'title', 'content', 'created_at', 'updated_at', 'sub_notes')



