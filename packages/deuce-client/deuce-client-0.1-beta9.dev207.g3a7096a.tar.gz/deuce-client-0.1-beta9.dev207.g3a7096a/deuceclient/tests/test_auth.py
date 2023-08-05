"""
Tests - Deuce Client - Auth - Authentication Base
"""
import abc
import mock
import uuid

import deuceclient.auth.base


class AuthenticationBaseTest(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_authengine(self, userid=None, usertype=None,
                          credentials=None, auth_method=None,
                          datacenter=None, auth_url=None):
        return NotImplementedError()

    def create_userid(self):
        return 'userid_{0:}'.format(str(uuid.uuid4()))

    def create_username(self):
        return 'username_{0:}'.format(str(uuid.uuid4()))

    def create_tenant_name(self):
        return 'tenantname_{0:}'.format(str(uuid.uuid4()))

    def create_tenant_id(self):
        return 'tenantid_{0:}'.format(str(uuid.uuid4()))

    def create_apikey(self):
        return 'apikey_{0:}'.format(str(uuid.uuid4()))

    def create_password(self):
        return 'password_{0:}'.format(str(uuid.uuid4()))

    def create_token(self):
        return 'token_{0:}'.format(str(uuid.uuid4()))

    def test_ancestory(self):
        authengine = self.create_authengine(userid=self.create_userid(),
                                            usertype='user_id',
                                            credentials=self.create_apikey(),
                                            auth_method='apikey',
                                            datacenter='test',
                                            auth_url='ancestory')

        self.assertIsInstance(authengine,
                              deuceclient.auth.base.AuthenticationBase)

        self.assertIsInstance(authengine,
                              object)

    def test_parameter_required(self):

        userid = self.create_userid()
        apikey = self.create_apikey()

        with self.assertRaises(deuceclient.auth.base.AuthenticationError) \
                as auth_error:

            authengine = self.create_authengine(userid=None,
                                                usertype='user_id',
                                                credentials=apikey,
                                                auth_method='apikey',
                                                datacenter='test',
                                                auth_url='ancestory')
            self.assertIn('userid', auth_error. str(auth_error))

        with self.assertRaises(deuceclient.auth.base.AuthenticationError) \
                as auth_error:

            authengine = self.create_authengine(userid=userid,
                                                usertype=None,
                                                credentials=apikey,
                                                auth_method='apikey',
                                                datacenter='test',
                                                auth_url='ancestory')
            self.assertIn('usertype', auth_error. str(auth_error))

        with self.assertRaises(deuceclient.auth.base.AuthenticationError) \
                as auth_error:

            authengine = self.create_authengine(userid=userid,
                                                usertype='user_id',
                                                credentials=None,
                                                auth_method='apikey',
                                                datacenter='test',
                                                auth_url='ancestory')
            self.assertIn('credentials', auth_error. str(auth_error))

        with self.assertRaises(deuceclient.auth.base.AuthenticationError) \
                as auth_error:

            authengine = self.create_authengine(userid=userid,
                                                usertype='user_id',
                                                credentials=apikey,
                                                auth_method=None,
                                                datacenter='test',
                                                auth_url='ancestory')
            self.assertIn('auth_method', auth_error. str(auth_error))

    def test_properties(self):
        user_data = [
            ('user_id', self.create_userid()),
            ('user_name', self.create_username())
        ]
        auth_data = [
            ('apikey', self.create_apikey()),
            ('password', self.create_password()),
            ('token', self.create_token())
        ]

        datacenter = 'dc_test'
        url = 'properties'

        for user in user_data:
            for auth in auth_data:
                authengine = self.create_authengine(userid=user[1],
                                                    usertype=user[0],
                                                    credentials=auth[1],
                                                    auth_method=auth[0],
                                                    datacenter=datacenter,
                                                    auth_url=url)

                self.assertEqual(authengine.usertype, user[0])
                self.assertEqual(authengine.userid, user[1])

                self.assertEqual(authengine.authmethod, auth[0])
                self.assertEqual(authengine.credentials, auth[1])

                self.assertEqual(authengine.datacenter, datacenter)
                self.assertEqual(authengine.authurl, url)
