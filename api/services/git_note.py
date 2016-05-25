# -*- coding: utf-8 -*-

import logging
import itertools
from os import mkdir
from datetime import datetime
from django.conf import settings
from git import Repo
from tzlocal import get_localzone

__author__ = 'JeOam'

def create_git_repo(uuid_str):
    """
    创建一个代码仓库
    :return:
    """
    git_path = settings.GIT_REPO_LOCATION + uuid_str
    try:
        mkdir(git_path)
    except FileExistsError:
        logging.warning("create git repo {} failed: already exist".format(
            git_path
        ))
    else:
        logging.info("create git repo at: {}".format(git_path))
        Repo.init(git_path)

def note_history(uuid_str, note_uuid_str, commit_count):
    """
    查询 Git 下某文件的历史版本
    """
    git_path = settings.GIT_REPO_LOCATION + uuid_str
    file_path = git_path + '/' + note_uuid_str
    repo = Repo(git_path)

    commits = list(repo.iter_commits(paths=file_path, max_count=commit_count))
    commit_diff_list = []
    for commit1, commit2 in zip(commits, commits[1:]):
        commit_diff_list.append(repo.git.diff(commit2, commit1))

def git_commit_list(uuid_str, begin=2, end=10):
    """
    获取 commit 列表数据，数据元素为：
    {
        "committer_name":
        "committer_email":
        "commit_date":
        "commit_hash":
        "commit_message":
    }
    :param uuid_str:
    :return:
    """
    git_path = settings.GIT_REPO_LOCATION + uuid_str
    repo = Repo(git_path)
    commit_info_list = []
    for commit in itertools.islice(repo.iter_commits(), begin, end):
        commit_info_list.append(
            {
                "committer_name": commit.committer.name,
                "committer_email": commit.committer.email,
                "commit_date": datetime.fromtimestamp(
                    commit.committed_date,
                    tz=get_localzone()
                ),
                "commit_hash": commit.hexsha,
                "commit_message": commit.message
            }
        )
    return commit_info_list
