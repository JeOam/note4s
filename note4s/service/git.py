# -*- coding: utf-8 -*-

"""
    git.py
    ~~~~~~~
"""
import logging
import os
from git import Repo
from note4s import settings


def create_git_repo(user_id):
    """
    创建一个代码仓库
    :return:
    """
    git_path = settings.GIT_DIR + user_id
    if not os.path.exists(git_path):
        os.mkdir(git_path)
        Repo.init(git_path)


def edit_git_note(user_id, note_id, content):
    """
    已有此 ID 文件则更新，没有则新建
    """
    create_git_repo(user_id)
    git_path = settings.GIT_DIR + user_id
    file_path = f'{git_path}/{note_id}.md'
    file = open(file_path, 'w+')
    file.write(content)
    file.close()
    repo = Repo(git_path)
    repo.index.add([f"{note_id}.md"])
    repo.index.commit(f"edit note {note_id}")


def delete_git_note(user_id, note_id):
    """
    删除某 note 对应的文件
    :return:
    """
    git_path = settings.GIT_DIR + user_id
    file_path = f'{git_path}/{note_id}.md'
    os.remove(file_path)
    repo = Repo(git_path)
    repo.index.remove([f"{note_id}.md"])
    repo.index.commit(f"delete note {note_id}")


def get_note_revision_count(user_id, note_id):
    """
    查询更新次数
    """
    git_path = settings.GIT_DIR + user_id
    repo = Repo(git_path)
    count = len(list(repo.iter_commits(paths=f"{note_id}.md")))
    if count > 0:
        count -= 1
    return count


def get_note_history(user_id, note_id, commit_count=10):
    """
    查询 Git 下某文件的历史版本
    """
    git_path = settings.GIT_DIR + user_id
    repo = Repo(git_path)
    commits = list(repo.iter_commits(paths=f"{note_id}.md", max_count=commit_count))
    commit_diffs = []
    for commit1, commit2 in zip(commits, commits[1:]):
        commit_diffs.append(repo.git.diff(commit2, commit1))
    return commit_diffs
