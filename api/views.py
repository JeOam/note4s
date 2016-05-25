# -*- coding: utf-8 -*-

from rest_framework import viewsets
from rest_framework import permissions

from .serializers import UserSerializer, NoteSerializer, SubNoteSerializer
from .models import CustomUser, Note, SubNote
from .permissions import IsOwnerOrReadOnly


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)

class SubNoteViewSet(viewsets.ModelViewSet):
    queryset = SubNote.objects.all()
    serializer_class = SubNoteSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)