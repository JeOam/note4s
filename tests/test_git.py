# -*- coding: utf-8 -*-

"""
    test_git.py
    ~~~~~~~
"""
import os
import shutil
from note4s import settings
from note4s.service.git import (
    create_git_repo,
    edit_git_note,
    get_note_history,
    delete_git_note
)

def test_create_git_repo():
    create_git_repo("test_user_id")
    assert os.path.exists(settings.GIT_DIR + "test_user_id")
    shutil.rmtree(settings.GIT_DIR + "test_user_id", ignore_errors=True)


def test_edit_git_note():
    create_git_repo("test_user_id")
    edit_git_note("test_user_id", "test_note_id", "test note content 1")
    with open(f"{settings.GIT_DIR}test_user_id/test_note_id.md") as f:
        content = f.read()
        assert content == "test note content 1"
    edit_git_note("test_user_id", "test_note_id", "test note content 2")
    with open(f"{settings.GIT_DIR}test_user_id/test_note_id.md") as f:
        content = f.read()
        assert content == "test note content 2"
    diffs = get_note_history("test_user_id", "test_note_id", 10)
    assert len(diffs) == 1
    for diff in diffs:
        assert diff["user"] == "note4s"
        assert diff["diff"].startswith("diff --git a/test_note_id.md b/test_note_id.md\n")
    shutil.rmtree(settings.GIT_DIR + "test_user_id", ignore_errors=True)


def test_delete_git_note():
    create_git_repo("test_user_id")
    edit_git_note("test_user_id", "test_note_id_1", "test note content")
    edit_git_note("test_user_id", "test_note_id_2", "test note content")
    delete_git_note("test_user_id", "test_note_id_2")
    assert os.path.exists(settings.GIT_DIR + "test_user_id/test_note_id_1.md")
    assert not os.path.exists(settings.GIT_DIR + "test_user_id/test_note_id_2.md")
    shutil.rmtree(settings.GIT_DIR + "test_user_id", ignore_errors=True)
