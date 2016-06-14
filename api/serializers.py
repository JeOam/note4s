# -*- coding: utf-8 -*-

"""
    serializers.py
    ~~~~~~~
    * Copyright (C) 2016 GridSafe, Inc.
"""
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_auth.serializers import UserDetailsSerializer

from .models import CustomUser, Note, SubNote, NoteBook, NoteSection


class PureNoteSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField(source="uuid_str", required=False)

    class Meta:
        model = Note
        fields = ('uuid', 'title', 'created_at', 'updated_at')


class NoteSectionSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField(source="uuid_str", required=False)
    notebook_uuid = serializers.UUIDField(source="notebook.uuid_str", write_only=True)
    notes = PureNoteSerializer(many=True, required=False)

    class Meta:
        model = NoteSection
        fields = ('uuid', 'notebook_uuid', 'name', 'notes')

    def create(self, validated_data):
        notebook = NoteBook.objects.filter(uuid=validated_data["notebook"]["uuid_str"]).first()
        validated_data["notebook"] = notebook
        return super(NoteSectionSerializer, self).create(validated_data)


class NoteBookSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField(source="uuid_str", required=False)
    note_sections = NoteSectionSerializer(many=True, required=False)

    class Meta:
        model = NoteBook
        fields = ('uuid', 'name', 'note_sections')

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data["custom_user"] = CustomUser.objects.filter(user=user).first()
        return super(NoteBookSerializer, self).create(validated_data)


class CustomUserSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField(source="uuid_str", required=False)
    username = serializers.SerializerMethodField()
    notebooks = NoteBookSerializer(many=True, read_only=True)

    def get_username(self, obj):
        return obj.user.username

    class Meta:
        model = CustomUser
        fields = ('uuid', 'username', 'avatar', 'notebooks')


class SubNoteSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField(source="uuid_str", required=False)
    note_uuid = serializers.UUIDField(source="note.uuid_str")

    class Meta:
        model = SubNote
        fields = ('uuid', 'note_uuid', 'content', 'created_at', 'updated_at')

    def create(self, validated_data):
        note = Note.objects.filter(pk=validated_data["note"]["uuid_str"]).first()
        if note is None:
            raise ValidationError({
                "note_uuid": ["Invalid note_uuid"]
            })
        validated_data["note"] = note
        return super(SubNoteSerializer, self).create(validated_data)


class NoteSerializer(serializers.ModelSerializer):
    uuid = serializers.CharField(source="uuid_str", required=False)
    sub_notes = SubNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = ('uuid', 'title', 'content', 'created_at', 'updated_at', 'sub_notes')

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data["custom_user"] = CustomUser.objects.filter(user=user).first()
        return super(NoteSerializer, self).create(validated_data)


class UserDetailSerializer(UserDetailsSerializer):
    avatar = serializers.CharField(source="custom_user.avatar")

    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + ('avatar',)

    def update(self, instance, validated_data):
        avatar = validated_data.pop('avatar', None)

        instance = super(UserDetailSerializer, self).update(instance, validated_data)

        # get and update user profile
        custom_user = instance.custom_user
        if avatar:
            custom_user.avatar = avatar
            custom_user.save()
        return instance
