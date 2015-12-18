# coding=utf-8

from django.shortcuts import render_to_response
from django.http import HttpResponse

from app.models import CustomUser, NoteBook, NoteSection, Note

__author__ = 'JeOam'


def hello(request):
    return HttpResponse("Hello, world.")

def index(request):
    custom_user = CustomUser.objects.get(user_id=request.user.id)
    note_books = NoteBook.objects.filter(custom_user__uuid=custom_user.uuid_str). \
        order_by('updated_at')
    if note_books:
        note_sessions = NoteSection.objects.filter(note_book__uuid=note_books[0].uuid_str)
        note_session_uuids = [note_session.uuid_str for note_session in note_sessions]
        notes = Note.objects.filter(note_section__uuid__in=note_session_uuids)
        session_note_dict = {}
        for note in notes:
            key = note.note_section
            note.link = "/note/{}".format(note.uuid_str)
            session_note_list = session_note_dict.get(key)
            if session_note_list:
                session_note_list.append(note)
            else:
                session_note_dict[key] = [note]

    context = {
        "title": "{}'s Notes".format(custom_user.nickname),
        "note_books": note_books,
        "session_note_dict": session_note_dict,
    }
    return render_to_response("app/index.html",
                              context=context)


def index_edit_notebook(request):
    """
    编辑 notebook 页面
    """
    return render_to_response("app/index.html")
