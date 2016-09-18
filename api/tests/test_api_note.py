# -*- coding: utf-8 -*-

"""
    test_api_note.py
    ~~~~~~~
    * Copyright (C) 2016 GridSafe, Inc.
"""
import pytest

@pytest.mark.django_db
@pytest.mark.usefixtures('client', 'token')
def test_create_note_visitor(client):
    response = client.post("/api/note/",
                           {
                               "title": "test_title",
                               "content": "test_content"
                           },
                           format='json')
    assert response.status_code == 200
    assert response.json()["code"] == 400


@pytest.mark.django_db
@pytest.mark.usefixtures('client', 'token')
def test_create_note(client, token):
    response = client.post("/api/note/",
                           {
                               "title": "test_title",
                               "content": "test_content",
                           },
                           format='json',
                           HTTP_AUTHORIZATION='Token {}'.format(token))
    assert response.status_code == 200  # Created
    assert response.json()["data"]["uuid"]


@pytest.mark.django_db
@pytest.mark.usefixtures('client', 'token', "test_note")
def test_get_note_detail(client, token, test_note):
    response = client.get("/api/note/" + test_note.uuid_str,
                          format='json',
                          HTTP_AUTHORIZATION='Token {}'.format(token))
    assert response.status_code == 200
    assert response.json()["data"]["title"] == "test_title"


@pytest.mark.django_db
@pytest.mark.usefixtures('client', 'token', "test_note")
def test_create_sub_note_success(client, token, test_note):
    response = client.post("/api/sub_note/",
                           {
                               "note_uuid": test_note.uuid_str,
                               "content": "test_content",
                           },
                           format='json',
                           HTTP_AUTHORIZATION='Token {}'.format(token))
    assert response.status_code == 200
    assert response.json()["data"]["note_uuid"] == test_note.uuid_str
    assert response.json()["data"]["content"] == "test_content"

    note_response = client.get("/api/note/" + test_note.uuid_str + "/",
                               format='json',
                               HTTP_AUTHORIZATION='Token {}'.format(token))
    assert note_response.status_code == 200
    assert note_response.json()["data"]["sub_notes"][0]["note_uuid"] == test_note.uuid_str


@pytest.mark.django_db
@pytest.mark.usefixtures('client', 'token', "test_note")
def test_create_sub_note_failed(client, token, test_note):
    response = client.post("/api/sub_note/",
                           {
                               "note_uuid": test_note.uuid_str[::-1],
                               "content": "test_content",
                           },
                           format='json',
                           HTTP_AUTHORIZATION='Token {}'.format(token))
    assert response.status_code == 200
    assert response.json()["code"] == 400
    assert response.json()["message"] == "子笔记出错"
