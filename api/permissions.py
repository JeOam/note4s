# -*- coding: utf-8 -*-

"""
    permissions.py
    ~~~~~~~
    * Copyright (C) 2016 GridSafe, Inc.
"""
from rest_framework import permissions
from api.models import Note

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet
        if isinstance(obj, Note):
            return obj.custom_user.user == request.user
        else:
            return obj.owner == request.user
