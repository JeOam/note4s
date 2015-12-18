# coding=utf-8

from django.shortcuts import render_to_response
from django.http import HttpResponse

from app.models import CustomUser, NoteBook, NoteSection

__author__ = 'JeOam'


def hello(request):
    return HttpResponse("Hello, world.")

def index(request):
    custom_user = CustomUser.objects.get(user_id=request.user.id)
    note_books = NoteBook.objects.filter(custom_user__uuid=custom_user.uuid_str). \
        order_by('updated_at')

    session = NoteSection.objects.filter(note_book_uuid=note_books.uuid_str)
    context = {
        "title": "{}'s Notes".format(custom_user.nickname),
        "note_books": note_books
    }
    return render_to_response("app/index.html",
                              context=context)


def index_edit_notebook(request):
    """
    编辑 notebook 页面
    """
    return render_to_response("app/index.html")
