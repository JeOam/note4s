# -*- coding: utf-8 -*-

"""
    organization.py
    ~~~~~~~
"""
from sqlalchemy import func
from .base import BaseRequestHandler
from note4s.models import Organization, Membership, O_ROLE, \
    Notebook, OWNER_TYPE, Watch, N_TARGET_TYPE, User
from note4s.service.notify import notify_organization_invite


class CheckNameHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        name = params.get("name", None)
        user = self.session.query(Organization).filter_by(name=name).all()
        if len(user) == 0:
            self.api_success_response(True)
        else:
            self.api_success_response(False)


class OrganizationHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        name = self.get_argument("name", None)
        organization = self.session.query(Organization).filter_by(name=name).first()
        if not organization:
            self.api_fail_response("organization name is invalid.")
            return
        result = organization.to_dict()
        membership = self.session.query(Membership).filter(
            Membership.organization_id == organization.id,
            Membership.user_id == self.current_user.id
        ).first()
        if membership:
            result["role"] = membership.role
        notebook_count = self.session.query(Notebook).filter(
            Notebook.owner_id == organization.id,
            Notebook.owner_type == OWNER_TYPE[1],
            Notebook.parent_id.is_(None)
        ).count()
        people_count = self.session.query(Membership).filter(
            Membership.role != O_ROLE[3]
        ).count()
        result["notebook_count"] = notebook_count
        result["people_count"] = people_count
        self.api_success_response(result)

    def post(self, *args, **kwargs):
        params = self.get_params()
        name = params.get("name")
        desc = params.get("desc")
        if not name:
            self.api_fail_response('Organization is required.')
            return

        organization = self.session.query(Organization).filter_by(name=name).first()
        if organization:
            self.api_fail_response("organization name is invalid.")
            return

        organization = Organization(
            name=name,
            desc=desc
        )
        membership = Membership(organization_id=organization.id,
                                user_id=self.current_user.id,
                                role=O_ROLE[0])
        self.session.add(organization)
        self.session.add(membership)
        self.session.commit()
        self.api_success_response(True)


class OrganizationsHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        if not self.current_user:
            self.api_fail_response("Authorization Required.", 401)
            return
        memberships = self.session.query(Membership).filter(
            Membership.user_id == self.current_user.id,
            Membership.role != O_ROLE[3]
        ).all()
        if memberships:
            organization_ids = [membership.organization_id for membership in memberships]
            organizations = self.session.query(Organization).filter(
                Organization.id.in_(organization_ids)
            ).all()
            organization_info = {}
            for organization in organizations:
                organization_info[organization.id] = organization.to_dict()
            result = []
            for membership in memberships:
                organization = organization_info[membership.organization_id]
                organization["role"] = membership.role
                result.append(organization)
        else:
            result = []
        self.api_success_response(result)


class NotebookHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        name = self.get_argument("name", None)
        organization = self.session.query(Organization).filter_by(name=name).first()
        if not organization:
            self.api_fail_response("organization name is invalid.")
            return
        notebooks = self.session.query(Notebook).filter(
            Notebook.owner_id == organization.id,
            Notebook.owner_type == OWNER_TYPE[1],
            Notebook.parent_id.is_(None)
        ).all()
        notebook_ids = [notebook.id for notebook in notebooks]
        watches = self.session.query(Watch.target_id, func.count(Watch.id)).filter(
            Watch.target_id.in_(notebook_ids),
            Watch.target_type == N_TARGET_TYPE[3]
        ).group_by(Watch.target_id).all()
        watch_info = {}
        for watch in watches:
            watch_info[watch[0]] = watch[1]
        result = []
        for notebook in notebooks:
            notebook_info = notebook.to_dict()
            notebook_info["watch_count"] = watch_info.get(notebook.id, 0)
            result.append(notebook_info)
        self.api_success_response(result)


class PeopleHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        name = self.get_argument("name", None)
        if not name:
            self.api_fail_response(f'name cannot be empty.')
            return
        organization = self.session.query(Organization).filter(Organization.name == name).first()
        if not organization:
            self.api_fail_response(f'Organization {name} does not exist.')
            return
        memberships = self.session.query(Membership).filter(
            Membership.organization_id == organization.id,
            Membership.role != O_ROLE[3]
        ).all()
        user_info = {}
        user_ids = []
        for membership in memberships:
            user_info[membership.user_id] = membership.role
            user_ids.append(membership.user_id)
        users = self.session.query(User).filter(
            User.id.in_(user_ids)
        ).all()
        result = []
        for user in users:
            tmp = user.to_dict()
            tmp["role"] = user_info[user.id]
            result.append(tmp)
        self.api_success_response(result)


class InviteHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        username = params.get("username")
        name = params.get("name")
        if not username or not name:
            self.api_fail_response(f'Username/Organization Name cannot be empty.')
            return
        organization = self.session.query(Organization).filter(Organization.name == name).first()
        if not organization:
            self.api_fail_response(f'Organization {name} does not exist.')
            return
        my_membership = self.session.query(Membership).filter(
            Membership.organization_id == organization.id,
            Membership.user_id == self.current_user.id
        ).first()
        if not my_membership or \
                (my_membership.role != O_ROLE[0] and my_membership.role != O_ROLE[1]):
            self.api_fail_response(f"You don't have the privilege to invite")
            return

        user = self.session.query(User).filter(User.username == username).first()
        if not organization:
            self.api_fail_response(f'User {username} does not exist.')

        membership = self.session.query(Membership).filter(
            Membership.organization_id == organization.id,
            Membership.user_id == user.id
        ).first()
        if not membership:
            membership = Membership(
                organization_id=organization.id,
                user_id=user.id,
                role=O_ROLE[3]
            )
            self.session.add(membership)
            self.session.commit()
            notify_organization_invite(
                organization_id=organization.id,
                organization_name=organization.name,
                receiver_id=user.id,
                sender_id=self.current_user.id,
                session=self.session
            )
        self.api_success_response(True)


class AcceptHandler(BaseRequestHandler):
    def post(self, *args, **kwargs):
        params = self.get_params()
        name = params.get("name")
        organization = self.session.query(Organization).filter(Organization.name == name).first()
        if not organization:
            self.api_fail_response(f'Organization {name} does not exist.')
            return
        membership = self.session.query(Membership).filter(
            Membership.organization_id == organization.id,
            Membership.user_id == self.current_user.id
        ).first()
        if membership:
            membership.role = O_ROLE[1]
            self.session.add(membership)
            self.session.commit()
            self.api_success_response(True)
        else:
            self.api_fail_response(False)


class CheckMembershipHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        name = self.get_argument("name", None)
        organization = self.session.query(Organization).filter(Organization.name == name).first()
        if not organization:
            self.api_fail_response(f'Organization {name} does not exist.')
            return
        membership = self.session.query(Membership).filter(
            Membership.organization_id == organization.id,
            Membership.user_id == self.current_user.id
        ).first()
        if membership and membership.role != O_ROLE[3]:
            self.api_success_response(True)
        else:
            self.api_success_response(False)
