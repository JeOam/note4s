# -*- coding: utf-8 -*-

"""
    user.py
    ~~~~~~~
"""
from datetime import datetime
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import exc
from sqlalchemy import func, desc, or_
from note4s.models import User, Watch, N_TARGET_TYPE, \
    UserNotification, Notification, N_ACTION, \
    Note
from note4s.utils import create_jwt
from .base import BaseRequestHandler


class LoginHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        email = params.get("email", None)
        password = params.get("password", None)
        if (not email) or (not password):
            self.api_fail_response("Not Enough Fields")
            return
        try:
            user = self.session.query(User).filter_by(email=email).one()
        except (exc.NoResultFound, exc.MultipleResultsFound) as e:
            self.api_fail_response('Login Failed. Please check you account and password.')
            return
        else:
            self.api_success_response(create_jwt(user.id.hex).decode("utf-8"))


class RegisterHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        username = params.get("username", None)
        email = params.get("email", None)
        password = params.get("password", None)
        if (not email) or (not password) or (not username):
            self.api_fail_response("Not Enough Fields")
            return

        user = User(username=username,
                    email=email,
                    password=generate_password_hash(password))
        try:
            self.session.add(user)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            self.api_fail_response("Failed to create user.")
        else:
            self.api_success_response(user.to_dict())


class CheckHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        username = params.get("username", None)
        user = self.session.query(User).filter_by(username=username).all()
        if len(user) == 0:
            self.api_success_response(True)
        else:
            self.api_success_response(False)


class MentionHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        name = self.get_argument("name")
        users = self.session.query(User).filter(
            or_(User.username.like(f"%{name}%"),
                User.nickname.like(f"%{name}%"))
        ).limit(10).all()
        self.api_success_response([user.to_dict(['username', 'nickname']) for user in users])


class ProfileHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        user = self.current_user
        self.api_success_response(user.to_dict())


class FollowHandler(BaseRequestHandler):
    def post(self, user_id):
        user = self.session.query(User).filter(User.id == user_id).first()
        if not user:
            self.api_fail_response(f'User {user_id} does not exist.')
            return

        watch = self.session.query(Watch).filter_by(
            target_id=user_id,
            target_type=N_TARGET_TYPE[0],
            user_id=self.current_user.id
        ).first()
        watch_count = self.session.query(Watch).filter_by(
            target_id=user_id,
            target_type=N_TARGET_TYPE[0]
        ).count()
        if watch:
            self.api_success_response(watch_count)
            return

        watch = Watch(target_id=user_id,
                      target_type=N_TARGET_TYPE[0],
                      user_id=self.current_user.id)
        self.session.add(watch)
        self.session.commit()
        self.api_success_response(watch_count + 1)

    def delete(self, user_id):
        user = self.session.query(User).filter(User.id == user_id).first()
        if not user:
            self.api_fail_response(f'User {user_id} does not exist.')
            return
        watch = self.session.query(Watch).filter_by(
            target_id=user_id,
            target_type=N_TARGET_TYPE[0],
            user_id=self.current_user.id
        ).first()
        self.session.delete(watch)
        self.session.commit()
        self.api_success_response(True)


class NotificationHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        user_notifications = self.session.query(
            UserNotification
        ).filter_by(
            user_id=self.current_user.id
        ).order_by(
            desc(UserNotification.created)
        ).all()
        result = {}
        stars = []
        follows = []
        generals = []
        unread_count = 0
        for user_notification in user_notifications:
            info = {}
            info["id"] = user_notification.notification_id.hex
            info["is_read"] = user_notification.is_read
            notification = self.session.query(Notification).filter_by(id=user_notification.notification_id).one()
            info["target_id"] = notification.target_id.hex
            info["target_type"] = notification.target_type
            info["target_desc"] = notification.target_desc
            info["action"] = notification.action
            info["sender_id"] = notification.sender_id.hex
            info["anchor"] = notification.anchor.hex if notification.anchor else ""
            sender = self.session.query(User).filter_by(id=notification.sender_id).one()
            info["sender_name"] = sender.username
            if (notification.action is N_ACTION[3]
                and notification.target_type is not N_TARGET_TYPE[0]) \
                    or notification.action is N_ACTION[4]:
                stars.append(info)
            elif (notification.action is N_ACTION[3]
                  and notification.target_type is N_TARGET_TYPE[0]):
                follows.append(info)
            else:
                generals.append(info)
            if not user_notification.is_read:
                unread_count += 1
        result["unread_count"] = unread_count
        result["generals"] = generals
        result["stars"] = stars
        result["follows"] = follows
        self.api_success_response(result)


class ContributionHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        begin = self.get_argument('begin', None)
        end = self.get_argument('end', None)
        username = self.get_argument('username', None)
        if not begin or not end:
            self.api_success_response({})
            return
        try:
            begin_date = datetime.strptime(begin, '%Y-%m-%d')
            end_date = datetime.strptime(end, '%Y-%m-%d')
        except ValueError:
            self.api_fail_response('Invalid begin or end date.')
            return
        else:
            end_date = end_date.replace(hour=23, minute=59, second=59)

        if not username:
            self.api_fail_response('username is required')
            return
        user = self.session.query(User).filter_by(username=username).first()
        if not user:
            self.api_fail_response(f'user {username} is invalid')
            return
        query_results = self.session.query(
            func.date_part('year', Note.created),
            func.date_part('month', Note.created),
            func.date_part('day', Note.created),
            func.count(Note.id)
        ).filter(
            Note.user == user,
            Note.created.between(begin_date, end_date)
        ).group_by(
            func.date_part('year', Note.created),
            func.date_part('month', Note.created),
            func.date_part('day', Note.created)
        ).all()
        result = {}
        for query_result in query_results:
            result[f'{str(int(query_result[0])).zfill(4)}-'
                   f'{str(int(query_result[1])).zfill(2)}-'
                   f'{str(int(query_result[2])).zfill(2)}'] = query_result[3]
        self.api_success_response(result)
