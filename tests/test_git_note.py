# -*- coding: utf-8 -*-

import shutil
from django.conf import settings
from git import Repo
from app.services import create_git_repo, note_history, \
    git_tag_list, git_commit_list

def test_create_git_repo():
    create_git_repo("uuid_str")
    git_path = settings.GIT_REPO_LOCATION + "uuid_str"
    repo = Repo(git_path)
    assert repo
    shutil.rmtree(git_path, ignore_errors=True)


def test_note_history(monkeypatch):
    # monkeypatch.setattr(settings, "GIT_REPO_LOCATION", '.')
    # note_history("test_git", "test.md", 50)
    test = git_commit_list("grid-cdnzz")
    import pytest
    pytest.set_trace()