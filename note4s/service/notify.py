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
    Watch, User, Note
)


def notify_new_note(note_owner_id, note_id, note_title, session):
    watches = session.query(Watch).filter_by(
        target_id=note_owner_id,
        target_type=N_TARGET_TYPE[0],
    ).all()
    if not len(watches):
        return
    notification = Notification(
        type=N_TYPE[0],
        target_id=note_id,
        target_type=N_TARGET_TYPE[1],
        target_desc=note_title,
        action=N_ACTION[0],
        sender_id=note_owner_id
    )
    session.add(notification)
    for watch in watches:
        user_notification = UserNotification(
            user_id=watch.user_id,
            notification_id=notification.id
        )
        session.add(user_notification)
    session.commit()


def notify_new_subnote(note_owner_id, note_id, subnote_id, session):
    watches = session.query(Watch).filter_by(
        target_id=note_id,
        target_type=N_TARGET_TYPE[1],
    ).all()
    if not len(watches):
        return
    note = session.query(Note).filter_by(id=note_id).one()
    notification = Notification(
        type=N_TYPE[0],
        target_id=note_id,
        target_type=N_TARGET_TYPE[1],
        target_desc=note.title,
        action=N_ACTION[1],
        sender_id=note_owner_id,
        anchor=subnote_id
    )
    session.add(notification)
    for watch in watches:
        user_notification = UserNotification(
            user_id=watch.user_id,
            notification_id=notification.id
        )
        session.add(user_notification)
    session.commit()



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


def notify_note_comment(note_owner_id, note_id, note_title, comment_id, sender_id, session):
    notification = Notification(
        type=N_TYPE[0],
        target_id=note_id,
        target_type=N_TARGET_TYPE[1],
        target_desc=note_title,
        action=N_ACTION[2],
        sender_id=sender_id,
        anchor=comment_id
    )
    user_notification = UserNotification(
        user_id=note_owner_id,
        notification_id=notification.id
    )
    session.add(notification)
    session.add(user_notification)
    session.commit()


def notify_comment_reply(to_user_id, comment_id, sender_id, session):
    # TODO: replace target_id with note_id
    notification = Notification(
        type=N_TYPE[0],
        target_id=comment_id,
        target_type=N_TARGET_TYPE[4],
        action=N_ACTION[6],
        sender_id=sender_id,
    )
    user_notification = UserNotification(
        user_id=to_user_id,
        notification_id=notification.id
    )
    session.add(notification)
    session.add(user_notification)
    session.commit()


def notify_comment_star(comment_owner_id, note_id, note_title, comment_id, sender_id, session):
    notification = Notification(
        type=N_TYPE[0],
        target_id=note_id,
        target_type=N_TARGET_TYPE[4],
        target_desc=note_title,
        action=N_ACTION[3],
        sender_id=sender_id,
        anchor=comment_id,
    )
    user_notification = UserNotification(
        user_id=comment_owner_id,
        notification_id=notification.id
    )
    session.add(notification)
    session.add(user_notification)
    session.commit()


def notify_comment_mention(note_id, note_title, comment_id, mentions, sender_id, session):
    notification = Notification(
        type=N_TYPE[0],
        target_id=note_id,
        target_type=N_TARGET_TYPE[4],
        target_desc=note_title,
        action=N_ACTION[5],
        sender_id=sender_id,
        anchor=comment_id,
    )
    session.add(notification)
    count = 0
    for username in mentions:
        try:
            user = session.query(User).filter_by(username=username).one()
        except:
            continue
        else:
            user_notification = UserNotification(
                user_id=user.id,
                notification_id=notification.id
            )
            session.add(user_notification)
            count += 1
    if count > 0:
        session.commit()


def notify_user_follow(user_id, sender_id, session):
    notification = Notification(
        type=N_TYPE[0],
        target_id=user_id,
        target_type=N_TARGET_TYPE[0],
        action=N_ACTION[4],
        sender_id=sender_id
    )
    user_notification = UserNotification(
        user_id=user_id,
        notification_id=notification.id
    )
    session.add(notification)
    session.add(user_notification)
    session.commit()