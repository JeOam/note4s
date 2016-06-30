# -*- coding: utf-8 -*-

from rest_framework import viewsets
from rest_framework import permissions

from .serializers import CustomUserSerializer, NoteBookSerializer, NoteSectionSerializer, NoteSerializer, SubNoteSerializer
from .models import CustomUser, NoteBook, NoteSection, Note, SubNote
from .permissions import IsOwnerOrReadOnly


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly)

class NotebookViewSet(viewsets.ModelViewSet):
    queryset = NoteBook.objects.all()
    serializer_class = NoteBookSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwnerOrReadOnly)

class NoteSectionViewSet(viewsets.ModelViewSet):
    queryset = NoteSection.objects.all()
    serializer_class = NoteSectionSerializer
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