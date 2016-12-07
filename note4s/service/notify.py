# -*- coding: utf-8 -*-

"""
    notify.py
    ~~~~~~~
    创建消息，放进队列，入库，生成缓存
    1. 评论了你的 Note
    2. 回复了你的评论
    3. @ 你 了
    4. 私信你了
    5. 点赞了你的 Note
    6. 发了站内消息
"""
from note4s.models import (
    Notification, N_TYPE,
    UserNotification
)

def notify_note_comment():
    pass


def create_remind(target_id, target_type, action, sender_id, session):
    notification = Notification(target_id=target_id,
                                target_type=target_type,
                                action=action,
                                type=N_TYPE[0])
    session.add(notification)
    session.commit()


def create_announce(content, sender_id, session):
    notification = Notification(content=content,
                                type=N_TYPE[1],
                                sender_id=sender_id)

    session.add(notification)
    session.commit()


def create_message(content, target_id, sender_id, session):
    notification = Notification(content=content,
                                target_id=target_id,
                                sender_id=sender_id,
                                type=N_TYPE[2])
    user_noficiation = UserNotification(user_id=target_id,
                                        notification_id=notification.id)
    session.add(notification)
    session.add(user_noficiation)
    session.commit()

def pull_notifications(user_id):
    pass


def read(user_id, notification_id):
    pass