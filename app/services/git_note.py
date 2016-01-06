# -*- coding: utf-8 -*-

from os import mkdir
import logging
from django.conf import settings
from git import Repo

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
