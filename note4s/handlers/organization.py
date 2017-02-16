# -*- coding: utf-8 -*-

"""
    organization.py
    ~~~~~~~
"""
from sqlalchemy import func
from .base import BaseRequestHandler
from note4s.models import Organization, Membership, O_ROLE, \
    Notebook, OWNER_TYPE, Watch, N_TARGET_TYPE


class CheckHandler(BaseRequestHandler):
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
        memberships = self.session.query(Membership).filter(
            Membership.user_id == self.current_user.id,
            Membership.role != O_ROLE[2]
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
        if watches:
            import pytest
            pytest.set_trace()
        self.api_success_response([notebook.to_dict() for notebook in notebooks])
