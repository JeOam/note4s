# -*- coding: utf-8 -*-

"""
    organization.py
    ~~~~~~~
"""
from .base import BaseRequestHandler
from note4s.models import Organization, Membership, O_ROLE


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
