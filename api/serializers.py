# -*- coding: utf-8 -*-

"""
    serializers.py
    ~~~~~~~
    * Copyright (C) 2016 GridSafe, Inc.
"""
from rest_framework import serializers
from rest_auth.serializers import UserDetailsSerializer
from rest_auth.registration.serializers import RegisterSerializer
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



class CustomUserSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    notebooks = NoteBookSerializer(many=True, read_only=True)

    def get_username(self, obj):
        return obj.user.username

    class Meta:
        model = CustomUser
        fields = ('uuid_str', 'username', 'avatar', 'notebooks')


class SubNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubNote
        fields = ('uuid_str', 'content', 'created_at', 'updated_at')


class NoteSerializer(serializers.ModelSerializer):
    sub_notes = SubNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = ('uuid_str', 'title', 'content', 'created_at', 'updated_at', 'sub_notes')


class CustomRegisterSerializer(RegisterSerializer):
    def custom_signup(self, request, user):
        custom_user = CustomUser(user=user)
        custom_user.save()


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
