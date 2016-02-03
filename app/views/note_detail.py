# coding=utf-8

from django.shortcuts import render_to_response, get_object_or_404
from app.models import Note
from app.services import markdown

__author__ = 'JeOam'

def note_detail(request, uuid_str):
    """
    返回笔记详情页
    """
    note = get_object_or_404(Note, pk=uuid_str)
    context = {
        "note_content": markdown(note.content)
    }
    return render_to_response("app/note_detail.html",
                              context=context)
