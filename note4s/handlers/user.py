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
    Note, Notebook, OWNER_TYPE, Star, Activity, \
    Organization, Membership
from note4s.utils import create_jwt, sent_mail, \
    is_valid_email, random_with_N_digits, redis
from note4s.service.notify import notify_user_follow
from note4s.service.feed import feed_follow_user
from note4s.service.git import create_git_repo
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
            timestamp, token = create_jwt(user.id.hex)
            user.token_time = timestamp
            self.session.add(user)
            self.session.commit()
            self.api_success_response(token.decode("utf-8"))


class RegisterHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        username = params.get("username")
        email = params.get("email")
        password = params.get("password")
        code = params.get("code")
        if (not email) or (not password) or (not username) or (not code):
            self.api_fail_response("Not Enough Fields")
            return
        user = self.session.query(User).filter_by(username=username).first()
        if user:
            self.api_fail_response("username is invalid.")
            return
        cache_code = redis.get(f'registration_code_{email}')
        if not cache_code or (code != cache_code.decode()):
            self.api_fail_response("verify code is invalid.")
            return
        user = User(username=username,
                    email=email,
                    password=generate_password_hash(password))
        self.session.add(user)
        self.session.commit()
        create_git_repo(user.id.hex)
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


class VerifyCodeHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        email = params.get("email", None)
        if not email:
            self.api_fail_response("email cannot be empty.")
            return
        if not is_valid_email(email):
            self.api_fail_response("email is invalid")
            return
        with open('note4s/utils/registration_code.html') as f:
            content = f.read()
            code = random_with_N_digits(6)
            redis.set(f'registration_code_{email}', code, 1800)
            content = content.replace('registration_code', str(code))
            sent_mail(
                from_mail='Note4s <no-reply@note4s.com>',
                to_mail=email,
                title="Verify your email address",
                content=content
            )
            self.api_success_response(True)


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
        if not self.current_user:
            self.api_success_response({})
            return
        username = self.get_argument("username", None)
        if username:
            user = self.session.query(User).filter_by(username=username).first()
            if not user:
                self.api_fail_response(f'User {username} does not exist.')
                return
        else:
            user = self.current_user

        result = user.to_dict()
        notebook_count = self.session.query(Notebook).filter(
            Notebook.owner_id == user.id,
            Notebook.owner_type == OWNER_TYPE[0],
            Notebook.parent_id.is_(None)
        ).count()
        note_count = self.session.query(Note).filter(
            Note.user_id == user.id,
            Note.parent_id.is_(None)
        ).count()
        star_count = self.session.query(Star).filter(
            Star.user_id == user.id,
            or_(
                Star.target_type == N_TARGET_TYPE[1],
                Star.target_type == N_TARGET_TYPE[3],
            )
        ).count()
        follower_count = self.session.query(Watch).filter(
            Watch.target_id == user.id,
            Watch.target_type == N_TARGET_TYPE[0],
            Watch.user_id != user.id
        ).count()
        following_count = self.session.query(Watch).filter(
            Watch.target_id != user.id,
            Watch.target_type == N_TARGET_TYPE[0],
            Watch.user_id == user.id,
        ).count()
        if username and self.current_user.username != username:
            followed = self.session.query(Watch).filter(
                Watch.target_id == user.id,
                Watch.target_type == N_TARGET_TYPE[0],
                Watch.user_id == self.current_user.id
            ).count()
            result["followed"] = True if followed else False
        result["notebook_count"] = notebook_count
        result["note_count"] = note_count
        result["star_count"] = star_count
        result["follower_count"] = follower_count
        result["following_count"] = following_count

        memberships = self.session.query(Membership).filter(
            Membership.user_id == self.current_user.id
        ).all()
        if memberships:
            organization_ids = [membership.organization_id for membership in memberships]
            organizations = self.session.query(Organization).filter(
                Organization.id.in_(organization_ids)
            ).all()
            organization_info = {}
            for organization in organizations:
                organization_info[organization.id] = organization.to_dict(['name', 'desc', 'avatar'])
            organization_result = []
            for membership in memberships:
                organization = organization_info[membership.organization_id]
                organization["roll"] = membership.role
                organization_result.append(organization)
            result["organizations"] = organization_result
        else:
            result["organizations"] = []
        self.api_success_response(result)

    def put(self, *args, **kwargs):
        keys = set(['nickname', 'email', 'avatar'])
        self.update_modal(self.current_user, keys)
        self.session.commit()
        self.api_success_response(True)


class FollowHandler(BaseRequestHandler):
    def post(self):
        params = self.get_params()
        username = params.get("username", None)
        if not username:
            self.api_fail_response(f'username cannot be empty.')
            return
        user = self.session.query(User).filter(User.username == username).first()
        if not user:
            self.api_fail_response(f'User {username} does not exist.')
            return

        watch = self.session.query(Watch).filter_by(
            target_id=user.id,
            target_type=N_TARGET_TYPE[0],
            user_id=self.current_user.id
        ).first()
        if watch:
            self.api_success_response(True)
            return

        watch = Watch(target_id=user.id,
                      target_type=N_TARGET_TYPE[0],
                      user_id=self.current_user.id)
        self.session.add(watch)
        self.session.commit()
        notify_user_follow(user_id=user.id, sender_id=self.current_user.id, session=self.session)
        feed_follow_user(user_id=self.current_user.id, target_id=user.id, session=self.session)
        self.api_success_response(True)


class Unfollowandler(BaseRequestHandler):
    def post(self):
        params = self.get_params()
        username = params.get("username", None)
        if not username:
            self.api_fail_response(f'username cannot be empty.')
            return
        user = self.session.query(User).filter(User.username == username).first()
        if not user:
            self.api_fail_response(f'User {username} does not exist.')
            return
        watch = self.session.query(Watch).filter_by(
            target_id=user.id,
            target_type=N_TARGET_TYPE[0],
            user_id=self.current_user.id
        ).first()
        self.session.delete(watch)
        self.session.commit()
        self.api_success_response(True)


class StarHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        username = self.get_argument("username", None)
        if not username:
            self.api_fail_response(f'username cannot be empty.')
            return
        user = self.session.query(User).filter(User.username == username).first()
        if not user:
            self.api_fail_response(f'User {username} does not exist.')
            return
        note_ids = self.session.query(Star.target_id).filter(
            Star.target_type == N_TARGET_TYPE[1],
            Star.user_id == user.id
        ).all()
        if note_ids:
            note_ids = [item[0] for item in note_ids]
            notes = self.session.query(Note).filter(
                Note.id.in_(note_ids)
            ).all()
            notebook_ids = [note.notebook_id for note in notes]
            notebook_private_ids = self.session.query(Notebook.id).filter(
                Notebook.id.in_(notebook_ids),
                Notebook.private == True
            ).all()
            notebook_private_ids = [notebook_id[0] for notebook_id in notebook_private_ids]
            # TODO make sure notes is in order by note_ids
            notes = sorted(notes, key=lambda o: note_ids.index(o.id))
            result = [note.to_dict() for note in notes if note.notebook_id not in notebook_private_ids]
        else:
            result = []
        self.api_success_response(result)


class FollowerHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        username = self.get_argument("username", None)
        if not username:
            self.api_fail_response(f'username cannot be empty.')
            return
        user = self.session.query(User).filter(User.username == username).first()
        if not user:
            self.api_fail_response(f'User {username} does not exist.')
            return
        watch_ids = self.session.query(Watch.user_id).filter(
            Watch.target_id == user.id,
            Watch.target_type == N_TARGET_TYPE[0]
        ).all()
        watch_ids = [item[0] for item in watch_ids]
        if watch_ids:
            users = self.session.query(User).filter(User.id.in_(watch_ids)).all()
            result = [user.to_dict() for user in users]
        else:
            result = []
        self.api_success_response(result)


class FollowingHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        username = self.get_argument("username", None)
        if not username:
            self.api_fail_response(f'username cannot be empty.')
            return
        user = self.session.query(User).filter(User.username == username).first()
        if not user:
            self.api_fail_response(f'User {username} does not exist.')
            return
        watch_ids = self.session.query(Watch.target_id).filter(
            Watch.target_id != user.id,
            Watch.target_type == N_TARGET_TYPE[0],
            Watch.user_id == user.id,
        ).all()
        if watch_ids:
            watch_ids = [item[0] for item in watch_ids]
            users = self.session.query(User).filter(User.id.in_(watch_ids)).all()
            result = [user.to_dict() for user in users]
        else:
            result = []
        self.api_success_response(result)


class NotificationHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        if not self.current_user:
            return self.api_success_response([])
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
            if (notification.action is N_ACTION[3] or notification.action is N_ACTION[4]) \
                    and notification.target_type is not N_TARGET_TYPE[0]:
                stars.append(info)
            elif (notification.action is N_ACTION[4]
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
            self.api_fail_response(f'User {username} does not exist.')
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


class ActivityHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        if not self.current_user:
            self.api_fail_response("Authorization Required.", 401)
            return
        username = self.get_argument("username", None)
        if username:
            user = self.session.query(User).filter_by(username=username).first()
            if not user:
                self.api_fail_response(f'User {username} does not exist.')
                return
            activities = self.session.query(Activity).filter_by(
                user_id=user.id
            ).order_by(desc(Activity.created)).all()
            result = [activity.to_dict() for activity in activities]
            self.api_success_response(result)
        else:
            user = self.current_user
            watches = self.session.query(Watch.target_id).filter(
                Watch.target_id != user.id,
                Watch.target_type == N_TARGET_TYPE[0],
                Watch.user_id == user.id,
            ).all()
            watch_ids = [watch[0] for watch in watches]
            watch_ids.append(user.id)
            activities = self.session.query(Activity).filter(
                Activity.user_id.in_(watch_ids)
            ).order_by(
                desc(Activity.created)
            ).all()
            if not activities:
                self.api_success_response([])
                return
            user_ids = [activity.user_id for activity in activities]
            users = self.session.query(User).filter(User.id.in_(user_ids)).all()
            users_info = {user.id.hex: user for user in users}
            result = [activity.to_dict() for activity in activities]
            for activity in result:
                activity["user"] = users_info[activity["user_id"]].to_dict()
            self.api_success_response(result)
