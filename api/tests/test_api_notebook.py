# -*- coding: utf-8 -*-

"""
    test_api_notebook.py
    ~~~~~~~
    * Copyright (C) 2016 GridSafe, Inc.
"""
import pytest
from api.models import NoteBook


@pytest.mark.django_db
@pytest.mark.usefixtures('client')
def test_get_notebooks_visitor(client):
    response = client.get("/api/notebook/",
                          format='json')
    assert response.status_code == 200
    assert response.json()["message"] == '笔记本出错'

@pytest.mark.django_db
@pytest.mark.usefixtures('client', 'token')
def test_get_notebooks(client, token):
    response = client.get("/api/notebook/",
                          format='json',
                          HTTP_AUTHORIZATION='Token {}'.format(token))
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.usefixtures('client', 'token')
def test_create_notebook(client, token):
    response = client.post("/api/notebook/",
                           {
                               "name": "test_notebook_name"
                           },
                           format='json',
                           HTTP_AUTHORIZATION='Token {}'.format(token))
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "test_notebook_name"
    notebook = NoteBook.objects.get(pk=response.json()["data"]["uuid"])
    assert notebook.custom_user


@pytest.mark.django_db
@pytest.mark.usefixtures('client', 'token', 'test_notebook')
def test_create_note_section(client, token, test_notebook):
    response1 = client.post("/api/note_section/",
                           {
                               "notebook_uuid": test_notebook.uuid_str,
                               "name": "test_note_section_name",
                           },
                           format='json',
                           HTTP_AUTHORIZATION='Token {}'.format(token))

    assert response1.status_code == 200
    assert response1.data["data"]["name"] == "test_note_section_name"

    response2 = client.get("/api/notebook/",
                           format='json',
                           HTTP_AUTHORIZATION='Token {}'.format(token))
    assert response2.status_code
    assert response2.data["data"]["results"][0]["name"] == test_notebook.name
    assert len(response2.data["data"]["results"][0]["note_sections"]) == 1
    assert response2.data["data"]["results"][0]["note_sections"][0]["name"] == "test_note_section_name"
