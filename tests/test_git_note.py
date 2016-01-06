# -*- coding: utf-8 -*-

import shutil
from django.conf import settings
from git import Repo
from app.services import create_git_repo

def test_create_git_repo():
    create_git_repo("uuid_str")
    git_path = settings.GIT_REPO_LOCATION + "uuid_str"
    repo = Repo(git_path)
    assert repo
    import pytest
    pytest.set_trace()
    shutil.rmtree(git_path, ignore_errors=True)


