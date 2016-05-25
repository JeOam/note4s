# -*- coding: utf-8 -*-

"""
    serializers.py
    ~~~~~~~
    * Copyright (C) 2016 GridSafe, Inc.
"""
from rest_framework import serializers
from .models import CustomUser, Note, SubNote, NoteBook, NoteSection


class UserSerializer(serializers.HyperlinkedModelSerializer):
    notebooks = serializers.HyperlinkedRelatedField(queryset=NoteBook.objects.all(),
                                                    view_name='notebooks',
                                                    many=True)

    class Meta:
        model = CustomUser
        fields = ('url', 'nickname', 'avatar', 'notebooks')


class NoteBookSerializer(serializers.HyperlinkedModelSerializer):
    note_sections = serializers.HyperlinkedRelatedField(queryset=NoteSection.objects.all(),
                                                        view_name='note_sections',
                                                        many=True)

    class Meta:
        model = NoteBook
        fields = ('url', 'uuid_str', 'name', 'note_sections')


class NoteSectionSerializer(serializers.HyperlinkedModelSerializer):
    notes = serializers.HyperlinkedRelatedField(queryset=Note.objects.all(),
                                                view_name='notes',
                                                many=True)

    class Meta:
        model = NoteSection
        fields = ('name', 'uuid_str', 'name', 'notes')


class NoteSerializer(serializers.HyperlinkedModelSerializer):
    sub_notes = serializers.HyperlinkedRelatedField(queryset=SubNote.objects.all(),
                                                    view_name="sub_notes",
                                                    many=True)

    class Meta:
        model = Note
        fields = ('url', 'uuid_str', 'title', 'content', 'created_at', 'updated_at', 'sub_notes')


class SubNoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SubNote
        fields = ('uuid_str', 'content', 'created_at', 'updated_at')
