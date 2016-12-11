# -*- coding: utf-8 -*-

"""
    notify.py
    ~~~~~~~
    创建消息，放进队列，入库，生成缓存
    1. 评论了你的 Note
    2. 回复了你的评论
    3. @ 你 了
    4. 私信你了
    5. Star 了你的 Note
    6. Watch 了你的 Note
    7. 发了站内消息
"""
from note4s.models import (
    Notification, N_TYPE, N_TARGET_TYPE, N_ACTION,
    UserNotification,
    Watch
)


def notify_new_note(user_id, note_id, note_title, session):
    watches = session.query(Watch).filter_by(
        target_id=user_id,
        target_type=N_TARGET_TYPE[0],
    ).all()
    notification = Notification(
        type=N_TYPE[0]
    )


def notify_note_star(note_owner_id, note_id, note_title, sender_id, session):
    notification = Notification(
        type=N_TYPE[0],
        target_id=note_id,
        target_type=N_TARGET_TYPE[1],
        target_desc=note_title,
        action=N_ACTION[3],
        sender_id=sender_id,
    )
    user_notification = UserNotification(
        user_id=note_owner_id,
        notification_id=notification.id
    )
    session.add(notification)
    session.add(user_notification)
    session.commit()


def notify_note_watch(note_owner_id, note_id, note_title, sender_id, session):
    notification = Notification(
        type=N_TYPE[0],
        target_id=note_id,
        target_type=N_TARGET_TYPE[1],
        target_desc=note_title,
        action=N_ACTION[4],
        sender_id=sender_id,
    )
    user_notification = UserNotification(
        user_id=note_owner_id,
        notification_id=notification.id
    )
    session.add(notification)
    session.add(user_notification)
    session.commit()


def notify_note_comment(note_owner_id, comment_id, sender_id, session):
    pass


def notify_note_comment_star(note_owner_id, comment_id, sender_id, session):
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
