"""
Deuce Non-Auth Authentication API

- Provides an auth plugin that does no authentication so one can run
deuceclient against an out-of-the-box Deuce instance
"""
import datetime
import logging

import deuceclient.auth


class NonAuthAuthentication(deuceclient.auth.AuthenticationBase):
    """
    Non-Auth Authentication for OOB Deuce Instances
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._args = args
        self._kwargs = kwargs
        self._token = "not_applicable_token"
        self._expires = datetime.datetime.max

    def GetToken(self, retry=5):
        return self._token

    def _AuthToken(self):
        return self._token

    def _AuthExpirationTime(self):
        return self._expires

    def IsExpired(self, fuzz=0):
        # This token never expires
        return False

    def _AuthTenantId(self):
        return self.userid
