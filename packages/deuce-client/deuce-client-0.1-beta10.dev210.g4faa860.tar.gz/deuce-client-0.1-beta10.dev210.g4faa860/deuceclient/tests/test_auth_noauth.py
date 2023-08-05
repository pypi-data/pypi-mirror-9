"""
Tests - Deuce Client - Auth - NonAuth Authentication
"""
import datetime
import random
from unittest import TestCase

import deuceclient.auth
import deuceclient.auth.nonauth as nonauth
import deuceclient.tests.test_auth


class NonAuthAuthTests(TestCase,
                       deuceclient.tests.test_auth.AuthenticationBaseTest):

    def setUp(self):
        super().setUp()

        self._userid = self.create_userid()
        self._apikey = self.create_apikey()

        self.authengine = self.create_authengine(userid=self._userid,
                                                 usertype='user_id',
                                                 credentials=self._apikey,
                                                 auth_method='apikey',
                                                 datacenter='test',
                                                 auth_url=None)

    def create_authengine(self, userid=None, usertype=None,
                          credentials=None, auth_method=None,
                          datacenter=None, auth_url=None):
        return nonauth.NonAuthAuthentication(userid=userid,
                                             usertype=usertype,
                                             credentials=credentials,
                                             auth_method=auth_method,
                                             datacenter=datacenter,
                                             auth_url=auth_url)

    def test_get_token(self):
        self.assertIsNotNone(self.authengine.GetToken())

    def test_auth_token(self):
        self.assertIsNotNone(self.authengine.AuthToken)

    def test_auth_expires(self):
        self.assertFalse(self.authengine.IsExpired())

    def test_auth_expires_after(self):
        fuzz = random.randint(1, 1000)

        self.assertFalse(self.authengine.IsExpired(fuzz=fuzz))

    def test_expires(self):
        self.assertEqual(datetime.datetime.max,
                         self.authengine.AuthExpirationTime)

    def test_tenantid(self):
        self.assertEqual(self._userid,
                         self.authengine.AuthTenantId)
