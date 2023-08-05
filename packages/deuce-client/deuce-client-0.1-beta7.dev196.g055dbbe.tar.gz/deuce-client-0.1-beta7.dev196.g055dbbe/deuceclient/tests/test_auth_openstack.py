"""
Tests - Deuce Client - Auth - OpenStack Authentication
"""
import datetime
import time
import uuid
from unittest import TestCase

import contextlib
import keystoneclient.exceptions
import mock

import deuceclient.auth
import deuceclient.auth.openstackauth as openstackauth
import deuceclient.tests.test_auth
from deuceclient.tests import fastsleep


class FakeAccess(object):
    """Fake Keystone Access Object for testing
    """
    raise_until = 0
    raise_counter = 0
    raise_error = False

    expire_time = None

    user_data = {
        'tenant': {
            'id': None,
            'name': None
        },
        'user': {
            'id': None,
            'name': None
        }
    }

    def __init__(self):
        pass

    @classmethod
    def raise_error(cls, raise_or_not):
        cls.raise_error = raise_or_not

    @classmethod
    def raise_reset(cls, raise_until=0, raise_error=False):
        cls.raise_until = raise_until
        cls.raise_error = raise_error
        cls.raise_counter = 0

    @property
    def tenant_id(self):
        if self.__class__.user_data['tenant']['id'] is None:
            raise RuntimeError('mocking')
        else:
            return self.__class__.user_data['tenant']['id']

    @property
    def tenant_name(self):
        if self.__class__.user_data['tenant']['name'] is None:
            raise RuntimeError('mocking')
        else:
            return self.__class__.user_data['tenant']['name']

    @property
    def user_id(self):
        if self.__class__.user_data['user']['id'] is None:
            raise RuntimeError('mocking')
        else:
            return self.__class__.user_data['user']['id']

    @property
    def username(self):
        if self.__class__.user_data['user']['name'] is None:
            raise RuntimeError('mocking')
        else:
            return self.__class__.user_data['user']['name']

    @property
    def auth_token(self):
        if self.__class__.raise_until > 0:
            self.__class__.raise_error = (
                self.__class__.raise_counter < self.__class__.raise_until)

            if self.__class__.raise_error:
                self.__class__.raise_counter = self.__class__.raise_counter + 1

        if self.__class__.raise_error is True:
            raise keystoneclient.exceptions.AuthorizationFailure('mocking')
        else:
            return 'token_{0:}'.format(str(uuid.uuid4()))

    @property
    def expires(self):
        if self.__class__.expire_time is None:
            print('Raising exception')
            raise keystoneclient.exceptions.AuthorizationFailure('mocking')
        else:
            print('Returning')
            return self.__class__.expire_time

    def will_expire_soon(self, stale_duration=None):
        if self.__class__.expire_time is None:
            # Expired already
            return True

        else:
            check_time = self.__class__.expire_time
            if stale_duration is not None:
                # otherwise we need to apply stale_duration and check
                check_time = check_time + \
                    datetime.timedelta(seconds=stale_duration)

            now_time = datetime.datetime.utcnow()

            return (check_time <= now_time)


class FakeClient(object):
    """Fake Keystone Client Object for testing
    """
    def __init__(self, *args, **kwargs):
        pass

    def get_raw_token_from_identity_service(self, *args, **kwargs):
        return FakeAccess()


class OpenStackAuthTest(TestCase,
                        deuceclient.tests.test_auth.AuthenticationBaseTest):
    def setUp(self):
        time.sleep = fastsleep

    keystone_discovery_version_data = [
        {
            "id": "v1.0",
            "links": [
                {
                    "href": "https://identity.api.rackspacecloud.com/"
                    "v1.0",
                    "rel": "self"
                }
            ],
            "status": "DEPRECATED",
            "updated": "2011-07-19T22:30:00Z"
        },
        {
            "id": "v1.1",
            "links": [
                {
                    "href": "http://docs.rackspacecloud.com/"
                    "auth/api/v1.1/auth.wadl",
                    "rel": "describedby",
                    "type": "application/vnd.sun.wadl+xml"
                }
            ],
            "status": "CURRENT",
            "updated": "2012-01-19T22:30:00.25Z"
        },
        {
            "id": "v2.0",
            "links": [
                {
                    "href":
                        "http://docs.rackspacecloud.com/"
                        "auth/api/v2.0/auth.wadl",
                    "rel": "describedby",
                    "type": "application/vnd.sun.wadl+xml"
                }
            ],
            "status": "CURRENT",
            "updated": "2012-01-19T22:30:00.25Z"
        }
    ]

    def create_authengine(self, userid=None, usertype=None,
                          credentials=None, auth_method=None,
                          datacenter=None, auth_url=None):
        return openstackauth.OpenStackAuthentication(userid=userid,
                                                     usertype=usertype,
                                                     credentials=credentials,
                                                     auth_method=auth_method,
                                                     datacenter=datacenter,
                                                     auth_url=auth_url)

    def test_parameter_no_authurl(self):
        userid = self.create_userid()
        apikey = self.create_apikey()

        with self.assertRaises(deuceclient.auth.AuthenticationError) \
                as auth_error:

            authengine = self.create_authengine(userid=userid,
                                                usertype='user_id',
                                                credentials=apikey,
                                                auth_method=None,
                                                datacenter='test',
                                                auth_url=None)

    def test_keystone_parameters(self):
        userid = self.create_userid()
        username = self.create_username()
        tenantid = self.create_tenant_id()
        tenantname = self.create_tenant_name()
        apikey = self.create_apikey()
        password = self.create_password()
        token = self.create_token()

        datacenter = 'test'
        auth_url = 'https://identity.api.rackspacecloud.com'

        usertype = 'user_id'
        auth_method = 'apikey'

        mok_ky_gen_client = 'keystoneclient.client.Client'
        mok_ky_v2_client = 'keystoneclient.v2_0.client.Client'

        with mock.patch(mok_ky_gen_client) as keystone_mock,\
                mock.patch(mok_ky_v2_client) as keystone_v2_client:
            keystone_mock.return_value = True
            keystone_v2_client.return_value = True

            authengine = self.create_authengine(userid=userid,
                                                usertype=usertype,
                                                credentials=apikey,
                                                auth_method=auth_method,
                                                datacenter=datacenter,
                                                auth_url=auth_url)

            client = authengine.get_client()

            try:
                kargs, kwargs = keystone_mock.call_args
            except TypeError:
                kargs, kwargs = keystone_v2_client.call_args

            self.assertIn('username', kwargs)
            self.assertEqual(kwargs['username'], userid)

            self.assertIn('password', kwargs)
            self.assertEqual(kwargs['password'], apikey)

            self.assertIn('auth_url', kwargs)
            self.assertEqual(kwargs['auth_url'], auth_url)

        usertype = 'user_name'
        auth_method = 'password'
        with mock.patch(mok_ky_gen_client) as keystone_mock,\
                mock.patch(mok_ky_v2_client) as keystone_v2_client:
            keystone_mock.return_value = True
            keystone_v2_client.return_value = True

            authengine = self.create_authengine(userid=username,
                                                usertype=usertype,
                                                credentials=password,
                                                auth_method=auth_method,
                                                datacenter=datacenter,
                                                auth_url=auth_url)

            client = authengine.get_client()

            try:
                kargs, kwargs = keystone_mock.call_args
            except TypeError:
                kargs, kwargs = keystone_v2_client.call_args

            self.assertIn('username', kwargs)
            self.assertEqual(kwargs['username'], username)

            self.assertIn('password', kwargs)
            self.assertEqual(kwargs['password'], password)

            self.assertIn('auth_url', kwargs)
            self.assertEqual(kwargs['auth_url'], auth_url)

        usertype = 'tenant_name'
        auth_method = 'token'
        with mock.patch(mok_ky_gen_client) as keystone_mock,\
                mock.patch(mok_ky_v2_client) as keystone_v2_client:
            keystone_mock.return_value = True
            keystone_v2_client.return_value = True

            authengine = self.create_authengine(userid=tenantname,
                                                usertype=usertype,
                                                credentials=token,
                                                auth_method=auth_method,
                                                datacenter=datacenter,
                                                auth_url=auth_url)

            client = authengine.get_client()

            try:
                kargs, kwargs = keystone_mock.call_args
            except TypeError:
                kargs, kwargs = keystone_v2_client.call_args

            self.assertIn('tenant_name', kwargs)
            self.assertEqual(kwargs['tenant_name'], tenantname)

            self.assertIn('token', kwargs)
            self.assertEqual(kwargs['token'], token)

            self.assertIn('auth_url', kwargs)
            self.assertEqual(kwargs['auth_url'], auth_url)

        usertype = 'tenant_id'
        auth_method = 'token'
        with mock.patch(mok_ky_gen_client) as keystone_mock,\
                mock.patch(mok_ky_v2_client) as keystone_v2_client:
            keystone_mock.return_value = True
            keystone_v2_client.return_value = True

            authengine = self.create_authengine(userid=tenantid,
                                                usertype=usertype,
                                                credentials=token,
                                                auth_method=auth_method,
                                                datacenter=datacenter,
                                                auth_url=auth_url)

            client = authengine.get_client()

            try:
                kargs, kwargs = keystone_mock.call_args
            except TypeError:
                kargs, kwargs = keystone_v2_client.call_args

            self.assertIn('tenant_id', kwargs)
            self.assertEqual(kwargs['tenant_id'], tenantid)

            self.assertIn('token', kwargs)
            self.assertEqual(kwargs['token'], token)

            self.assertIn('auth_url', kwargs)
            self.assertEqual(kwargs['auth_url'], auth_url)

        usertype = 'bison'
        with mock.patch(mok_ky_gen_client) as keystone_mock,\
                mock.patch(mok_ky_v2_client) as keystone_v2_client:
            keystone_mock.return_value = False
            keystone_v2_client.return_value = False

            authengine = self.create_authengine(userid=tenantid,
                                                usertype=usertype,
                                                credentials=token,
                                                auth_method=auth_method,
                                                datacenter=datacenter,
                                                auth_url=auth_url)

            with self.assertRaises(deuceclient.auth.base.AuthenticationError) \
                    as auth_error:

                client = authengine.get_client()

                self.assertIn('usertype', str(auth_error))

        usertype = 'tenant_id'
        auth_method = 'yak'
        with mock.patch(mok_ky_gen_client) as keystone_mock,\
                mock.patch(mok_ky_v2_client) as keystone_v2_client:
            keystone_mock.return_value = False
            keystone_v2_client.return_value = False

            authengine = self.create_authengine(userid=tenantid,
                                                usertype=usertype,
                                                credentials=token,
                                                auth_method=auth_method,
                                                datacenter=datacenter,
                                                auth_url=auth_url)

            with self.assertRaises(deuceclient.auth.base.AuthenticationError) \
                    as auth_error:

                client = authengine.get_client()

                self.assertIn('auth_method', str(auth_error))

    def test_get_token_invalid_client_username_password(self):
        usertype = 'user_name'
        username = self.create_username()

        apikey = self.create_apikey()
        auth_method = 'apikey'

        datacenter = 'test'
        auth_url = 'http://identity.api.rackspacecloud.com'

        with mock.patch(
            'deuceclient.auth.openstackauth.OpenStackAuthentication.get_client'
        ) as mok_get_client:
            mok_get_client.side_effect = \
                deuceclient.auth.AuthenticationError('mock')

            authengine = self.create_authengine(userid=username,
                                                usertype=usertype,
                                                credentials=apikey,
                                                auth_method=auth_method,
                                                datacenter=datacenter,
                                                auth_url=auth_url)

            with self.assertRaises(deuceclient.auth.AuthenticationError) \
                    as auth_error:
                authengine.GetToken(retry=0)

    def test_get_token_invalid_client_tenant_id_token(self):
        usertype = 'tenant_id'
        username = self.create_tenant_id()

        token = self.create_token()
        auth_method = 'token'

        datacenter = 'test'
        auth_url = 'http://identity.api.rackspacecloud.com'

        with mock.patch(
            'deuceclient.auth.openstackauth.OpenStackAuthentication.get_client'
        ) as mok_get_client:
            mok_get_client.side_effect = \
                deuceclient.auth.AuthenticationError('mock')

            authengine = self.create_authengine(userid=username,
                                                usertype=usertype,
                                                credentials=token,
                                                auth_method=auth_method,
                                                datacenter=datacenter,
                                                auth_url=auth_url)

            with self.assertRaises(deuceclient.auth.AuthenticationError) \
                    as auth_error:
                authengine.GetToken(retry=0)

    def test_get_token_failed(self):
        usertype = 'user_name'
        username = self.create_username()

        apikey = self.create_apikey()
        auth_method = 'apikey'

        datacenter = 'test'
        auth_url = 'http://identity.api.rackspacecloud.com'

        # Because the mock strings are so long, we're going to store them
        # in variables here to keep the mocking statements short
        mok_ky_base = 'keystoneclient'

        mok_ky_httpclient = '{0:}.httpclient.HTTPClient'.format(mok_ky_base)
        mok_ky_auth = '{0:}.authenticate'.format(mok_ky_httpclient)

        mok_ky_v2_client = '{0:}.v2_0.client.Client'.format(mok_ky_base)
        mok_ky_v2_rawtoken = '{0:}.get_raw_token_from_identity_service'\
            .format(mok_ky_v2_client)

        mok_ky_discover = '{0:}.discover'.format(mok_ky_base)
        mok_ky_discovery = '{0:}.Discover'.format(mok_ky_discover)
        mok_ky_discovery_init = '{0:}.__init__'.format(mok_ky_discovery)
        mok_ky_discover_client = '{0:}.create_client'.format(mok_ky_discovery)

        mok_ky_discover_int = '{0:}._discover'.format(mok_ky_base)
        mok_ky_discover_version = '{0:}.get_version_data'\
            .format(mok_ky_discover_int)

        with mock.patch(mok_ky_auth) as keystone_auth_mock,\
                mock.patch(mok_ky_v2_client) as keystone_v2_client,\
                mock.patch(mok_ky_v2_rawtoken) as keystone_raw_token_mock,\
                mock.patch(mok_ky_discover_version) as keystone_discover_ver,\
                mock.patch(mok_ky_discover_client) as keystone_discover_cli:

            keystone_auth_mock.return_value = True

            keystone_discover_ver.return_value = \
                self.keystone_discovery_version_data
            keystone_discover_cli.return_value = FakeClient()
            keystone_v2_client.return_value = FakeClient()

            FakeAccess.raise_until = 4
            FakeAccess.raise_counter = 0
            keystone_raw_token_mock.return_value = FakeAccess()

            authengine = self.create_authengine(userid=username,
                                                usertype=usertype,
                                                credentials=apikey,
                                                auth_method=auth_method,
                                                datacenter=datacenter,
                                                auth_url=auth_url)

            with self.assertRaises(deuceclient.auth.AuthenticationError) \
                    as auth_error:
                authengine.GetToken(retry=FakeAccess.raise_until - 1)

    def test_get_token_success_username_password(self):
        usertype = 'user_name'
        username = self.create_username()

        apikey = self.create_apikey()
        auth_method = 'apikey'

        datacenter = 'test'
        auth_url = 'http://identity.api.rackspacecloud.com'

        # Because the mock strings are so long, we're going to store them
        # in variables here to keep the mocking statements short
        mok_ky_base = 'keystoneclient'

        mok_ky_httpclient = '{0:}.httpclient.HTTPClient'.format(mok_ky_base)
        mok_ky_auth = '{0:}.authenticate'.format(mok_ky_httpclient)

        mok_ky_v2_client = '{0:}.v2_0.client.Client'.format(mok_ky_base)
        mok_ky_v2_rawtoken = '{0:}.get_raw_token_from_identity_service'\
            .format(mok_ky_v2_client)

        mok_ky_discover = '{0:}.discover'.format(mok_ky_base)
        mok_ky_discovery = '{0:}.Discover'.format(mok_ky_discover)
        mok_ky_discovery_init = '{0:}.__init__'.format(mok_ky_discovery)
        mok_ky_discover_client = '{0:}.create_client'.format(mok_ky_discovery)

        mok_ky_discover_int = '{0:}._discover'.format(mok_ky_base)
        mok_ky_discover_version = '{0:}.get_version_data'\
            .format(mok_ky_discover_int)

        with mock.patch(mok_ky_auth) as keystone_auth_mock,\
                mock.patch(mok_ky_v2_client) as keystone_v2_client,\
                mock.patch(mok_ky_v2_rawtoken) as keystone_raw_token_mock,\
                mock.patch(mok_ky_discover_version) as keystone_discover_ver,\
                mock.patch(mok_ky_discover_client) as keystone_discover_cli:

            keystone_auth_mock.return_value = True

            keystone_discover_ver.return_value = \
                self.keystone_discovery_version_data
            keystone_discover_cli.return_value = FakeClient()
            keystone_v2_client.return_value = FakeClient()

            FakeAccess.raise_until = 4
            FakeAccess.raise_counter = 0
            keystone_raw_token_mock.return_value = FakeAccess()

            authengine = self.create_authengine(userid=username,
                                                usertype=usertype,
                                                credentials=apikey,
                                                auth_method=auth_method,
                                                datacenter=datacenter,
                                                auth_url=auth_url)

            token = authengine.GetToken(retry=FakeAccess.raise_until)

    def test_get_token_success_tenantid_token(self):
        usertype = 'tenant_id'
        username = self.create_tenant_id()

        token = self.create_token()
        auth_method = 'token'

        datacenter = 'test'
        auth_url = 'http://identity.api.rackspacecloud.com'

        # Because the mock strings are so long, we're going to store them
        # in variables here to keep the mocking statements short
        mok_ky_base = 'keystoneclient'

        mok_ky_httpclient = '{0:}.httpclient.HTTPClient'.format(mok_ky_base)
        mok_ky_auth = '{0:}.authenticate'.format(mok_ky_httpclient)

        mok_ky_v2_client = '{0:}.v2_0.client.Client'.format(mok_ky_base)
        mok_ky_v2_rawtoken = '{0:}.get_raw_token_from_identity_service'\
            .format(mok_ky_v2_client)

        mok_ky_discover = '{0:}.discover'.format(mok_ky_base)
        mok_ky_discovery = '{0:}.Discover'.format(mok_ky_discover)
        mok_ky_discovery_init = '{0:}.__init__'.format(mok_ky_discovery)
        mok_ky_discover_client = '{0:}.create_client'.format(mok_ky_discovery)

        mok_ky_discover_int = '{0:}._discover'.format(mok_ky_base)
        mok_ky_discover_version = '{0:}.get_version_data'\
            .format(mok_ky_discover_int)

        with mock.patch(mok_ky_auth) as keystone_auth_mock,\
                mock.patch(mok_ky_v2_client) as keystone_v2_client,\
                mock.patch(mok_ky_v2_rawtoken) as keystone_raw_token_mock,\
                mock.patch(mok_ky_discover_version) as keystone_discover_ver,\
                mock.patch(mok_ky_discover_client) as keystone_discover_cli:

            keystone_auth_mock.return_value = True

            keystone_discover_ver.return_value = \
                self.keystone_discovery_version_data
            keystone_discover_cli.return_value = FakeClient()
            keystone_v2_client.return_value = FakeClient()

            FakeAccess.raise_until = 4
            FakeAccess.raise_counter = 0
            keystone_raw_token_mock.return_value = FakeAccess()

            authengine = self.create_authengine(userid=username,
                                                usertype=usertype,
                                                credentials=token,
                                                auth_method=auth_method,
                                                datacenter=datacenter,
                                                auth_url=auth_url)

            token = authengine.GetToken(retry=FakeAccess.raise_until)

    def test_is_expired_no_client(self):
        usertype = 'user_name'
        username = self.create_username()

        apikey = self.create_apikey()
        auth_method = 'apikey'

        datacenter = 'test'
        auth_url = 'http://identity.api.rackspacecloud.com'

        authengine = self.create_authengine(userid=username,
                                            usertype=usertype,
                                            credentials=apikey,
                                            auth_method=auth_method,
                                            datacenter=datacenter,
                                            auth_url=auth_url)

        self.assertTrue(authengine.IsExpired())

    def test_is_expired_result(self):
        usertype = 'user_name'
        username = self.create_username()

        apikey = self.create_apikey()
        auth_method = 'apikey'

        datacenter = 'test'
        auth_url = 'http://identity.api.rackspacecloud.com'

        # Because the mock strings are so long, we're going to store them
        # in variables here to keep the mocking statements short
        mok_ky_base = 'keystoneclient'

        mok_ky_httpclient = '{0:}.httpclient.HTTPClient'.format(mok_ky_base)
        mok_ky_auth = '{0:}.authenticate'.format(mok_ky_httpclient)

        mok_ky_v2_client = '{0:}.v2_0.client.Client'.format(mok_ky_base)
        mok_ky_v2_rawtoken = '{0:}.get_raw_token_from_identity_service'\
            .format(mok_ky_v2_client)

        mok_ky_discover = '{0:}.discover'.format(mok_ky_base)
        mok_ky_discovery = '{0:}.Discover'.format(mok_ky_discover)
        mok_ky_discovery_init = '{0:}.__init__'.format(mok_ky_discovery)
        mok_ky_discover_client = '{0:}.create_client'.format(mok_ky_discovery)

        mok_ky_discover_int = '{0:}._discover'.format(mok_ky_base)
        mok_ky_discover_version = '{0:}.get_version_data'\
            .format(mok_ky_discover_int)

        with mock.patch(mok_ky_auth) as keystone_auth_mock,\
                mock.patch(mok_ky_v2_client) as keystone_v2_client,\
                mock.patch(mok_ky_v2_rawtoken) as keystone_raw_token_mock,\
                mock.patch(mok_ky_discover_version) as keystone_discover_ver,\
                mock.patch(mok_ky_discover_client) as keystone_discover_cli:

            keystone_auth_mock.return_value = True

            keystone_discover_ver.return_value = \
                self.keystone_discovery_version_data
            keystone_discover_cli.return_value = FakeClient()
            keystone_v2_client.return_value = FakeClient()

            FakeAccess.raise_until = 4
            FakeAccess.raise_counter = 0
            keystone_raw_token_mock.return_value = FakeAccess()

            authengine = self.create_authengine(userid=username,
                                                usertype=usertype,
                                                credentials=apikey,
                                                auth_method=auth_method,
                                                datacenter=datacenter,
                                                auth_url=auth_url)

            token = authengine.GetToken(retry=FakeAccess.raise_until)
            FakeAccess.expire_time = None

            self.assertTrue(authengine.IsExpired())

            FakeAccess.expire_time = datetime.datetime.utcnow()

            self.assertFalse(authengine.IsExpired(fuzz=5))

            self.assertTrue(authengine.IsExpired())

            FakeAccess.expire_time = datetime.datetime.utcnow() + \
                datetime.timedelta(seconds=5)

            self.assertFalse(authengine.IsExpired())

            self.assertTrue(authengine.IsExpired(fuzz=-10))

            sleep_time = (datetime.datetime.utcnow() - FakeAccess.expire_time)\
                .total_seconds()

            if sleep_time > 0:
                time.sleep(sleep_time + 1)

            self.assertFalse(authengine.IsExpired())

            # We must reset expire_time when we're done
            FakeAccess.expire_time = None

    def test_auth_token_expired(self):
        usertype = 'user_name'
        username = self.create_username()

        apikey = self.create_apikey()
        auth_method = 'apikey'

        datacenter = 'test'
        auth_url = 'http://identity.api.rackspacecloud.com'

        authengine = self.create_authengine(userid=username,
                                            usertype=usertype,
                                            credentials=apikey,
                                            auth_method=auth_method,
                                            datacenter=datacenter,
                                            auth_url=auth_url)

        mok_isexpired = 'deuceclient.auth.openstackauth' \
            '.OpenStackAuthentication.IsExpired'
        mok_gettoken = 'deuceclient.auth.openstackauth' \
            '.OpenStackAuthentication.GetToken'

        with mock.patch(mok_isexpired) as mock_isexpired,\
                mock.patch(mok_gettoken) as mock_gettoken:

            mock_isexpired.return_value = True
            token = self.create_token()
            mock_gettoken.return_value = token

            self.assertEqual(token, authengine.AuthToken)

    def test_auth_token_will_expire(self):
        usertype = 'user_name'
        username = self.create_username()

        apikey = self.create_apikey()
        auth_method = 'apikey'

        datacenter = 'test'
        auth_url = 'http://identity.api.rackspacecloud.com'

        authengine = self.create_authengine(userid=username,
                                            usertype=usertype,
                                            credentials=apikey,
                                            auth_method=auth_method,
                                            datacenter=datacenter,
                                            auth_url=auth_url)

        mok_isexpired = 'deuceclient.auth.openstackauth' \
            '.OpenStackAuthentication.IsExpired'
        mok_gettoken = 'deuceclient.auth.openstackauth' \
            '.OpenStackAuthentication.GetToken'

        with mock.patch(mok_isexpired) as mock_isexpired,\
                mock.patch(mok_gettoken) as mock_gettoken:

            mock_isexpired.side_effect = [False, True]
            token = self.create_token()
            mock_gettoken.return_value = token

            self.assertEqual(token, authengine.AuthToken)

    def test_auth_token_cached(self):
        usertype = 'user_name'
        username = self.create_username()

        apikey = self.create_apikey()
        auth_method = 'apikey'

        datacenter = 'test'
        auth_url = 'http://identity.api.rackspacecloud.com'

        mok_isexpired = 'deuceclient.auth.openstackauth' \
            '.OpenStackAuthentication.IsExpired'
        mok_authtoken = 'deuceclient.auth.openstackauth' \
            '.OpenStackAuthentication.__access.auth_token'

        # Because the mock strings are so long, we're going to store them
        # in variables here to keep the mocking statements short
        mok_ky_base = 'keystoneclient'

        mok_ky_httpclient = '{0:}.httpclient.HTTPClient'.format(mok_ky_base)
        mok_ky_auth = '{0:}.authenticate'.format(mok_ky_httpclient)

        mok_ky_v2_client = '{0:}.v2_0.client.Client'.format(mok_ky_base)
        mok_ky_v2_rawtoken = '{0:}.get_raw_token_from_identity_service'\
            .format(mok_ky_v2_client)

        mok_ky_discover = '{0:}.discover'.format(mok_ky_base)
        mok_ky_discovery = '{0:}.Discover'.format(mok_ky_discover)
        mok_ky_discovery_init = '{0:}.__init__'.format(mok_ky_discovery)
        mok_ky_discover_client = '{0:}.create_client'.format(mok_ky_discovery)

        mok_ky_discover_int = '{0:}._discover'.format(mok_ky_base)
        mok_ky_discover_version = '{0:}.get_version_data'\
            .format(mok_ky_discover_int)

        with mock.patch(mok_ky_auth) as keystone_auth_mock,\
                mock.patch(mok_ky_v2_client) as keystone_v2_client,\
                mock.patch(mok_ky_v2_rawtoken) as keystone_raw_token_mock,\
                mock.patch(mok_ky_discover_version) as keystone_discover_ver,\
                mock.patch(mok_ky_discover_client) as keystone_discover_cli, \
                mock.patch(mok_isexpired) as mock_isexpired:

            keystone_auth_mock.return_value = True

            keystone_discover_ver.return_value = \
                self.keystone_discovery_version_data
            keystone_discover_cli.return_value = FakeClient()
            keystone_v2_client.return_value = FakeClient()

            FakeAccess.raise_until = 0
            FakeAccess.raise_counter = 0
            keystone_raw_token_mock.return_value = FakeAccess()

            mock_isexpired.return_value = False
            token = self.create_token()

            authengine = self.create_authengine(userid=username,
                                                usertype=usertype,
                                                credentials=apikey,
                                                auth_method=auth_method,
                                                datacenter=datacenter,
                                                auth_url=auth_url)

            # Setups up the __acccess node used by AuthToken for
            # non-expired functions
            authengine.GetToken()

            authengine.AuthToken

    def test_expiration_time(self):
        usertype = 'user_name'
        username = self.create_username()

        apikey = self.create_apikey()
        auth_method = 'apikey'

        datacenter = 'test'
        auth_url = 'http://identity.api.rackspacecloud.com'

        # Because the mock strings are so long, we're going to store them
        # in variables here to keep the mocking statements short
        mok_ky_base = 'keystoneclient'

        mok_ky_httpclient = '{0:}.httpclient.HTTPClient'.format(mok_ky_base)
        mok_ky_auth = '{0:}.authenticate'.format(mok_ky_httpclient)

        mok_ky_v2_client = '{0:}.v2_0.client.Client'.format(mok_ky_base)
        mok_ky_v2_rawtoken = '{0:}.get_raw_token_from_identity_service'\
            .format(mok_ky_v2_client)

        mok_ky_discover = '{0:}.discover'.format(mok_ky_base)
        mok_ky_discovery = '{0:}.Discover'.format(mok_ky_discover)
        mok_ky_discovery_init = '{0:}.__init__'.format(mok_ky_discovery)
        mok_ky_discover_client = '{0:}.create_client'.format(mok_ky_discovery)

        mok_ky_discover_int = '{0:}._discover'.format(mok_ky_base)
        mok_ky_discover_version = '{0:}.get_version_data'\
            .format(mok_ky_discover_int)

        with mock.patch(mok_ky_auth) as keystone_auth_mock,\
                mock.patch(mok_ky_v2_client) as keystone_v2_client,\
                mock.patch(mok_ky_v2_rawtoken) as keystone_raw_token_mock,\
                mock.patch(mok_ky_discover_version) as keystone_discover_ver,\
                mock.patch(mok_ky_discover_client) as keystone_discover_cli:

            keystone_auth_mock.return_value = True

            keystone_discover_ver.return_value = \
                self.keystone_discovery_version_data
            keystone_discover_cli.return_value = FakeClient()
            keystone_v2_client.return_value = FakeClient()

            keystone_raw_token_mock.return_value = FakeAccess()

            authengine = self.create_authengine(userid=username,
                                                usertype=usertype,
                                                credentials=apikey,
                                                auth_method=auth_method,
                                                datacenter=datacenter,
                                                auth_url=auth_url)

            token = authengine.GetToken(retry=FakeAccess.raise_until)
            FakeAccess.expire_time = None
            expire_time = authengine.AuthExpirationTime
            self.assertIsNotNone(expire_time)

            FakeAccess.expire_time = 'howdy'

            expire_time = authengine.AuthExpirationTime
            self.assertEqual(expire_time, FakeAccess.expire_time)

            FakeAccess.expire_time = None

    def test_user_data(self):
        usertype = 'user_name'
        username = self.create_username()

        apikey = self.create_apikey()
        auth_method = 'apikey'

        datacenter = 'test'
        auth_url = 'http://identity.api.rackspacecloud.com'

        # Because the mock strings are so long, we're going to store them
        # in variables here to keep the mocking statements short
        mok_ky_base = 'keystoneclient'

        mok_ky_httpclient = '{0:}.httpclient.HTTPClient'.format(mok_ky_base)
        mok_ky_auth = '{0:}.authenticate'.format(mok_ky_httpclient)

        mok_ky_v2_client = '{0:}.v2_0.client.Client'.format(mok_ky_base)
        mok_ky_v2_rawtoken = '{0:}.get_raw_token_from_identity_service'\
            .format(mok_ky_v2_client)

        mok_ky_discover = '{0:}.discover'.format(mok_ky_base)
        mok_ky_discovery = '{0:}.Discover'.format(mok_ky_discover)
        mok_ky_discovery_init = '{0:}.__init__'.format(mok_ky_discovery)
        mok_ky_discover_client = '{0:}.create_client'.format(mok_ky_discovery)

        mok_ky_discover_int = '{0:}._discover'.format(mok_ky_base)
        mok_ky_discover_version = '{0:}.get_version_data'\
            .format(mok_ky_discover_int)

        with mock.patch(mok_ky_auth) as keystone_auth_mock,\
                mock.patch(mok_ky_v2_client) as keystone_v2_client,\
                mock.patch(mok_ky_v2_rawtoken) as keystone_raw_token_mock,\
                mock.patch(mok_ky_discover_version) as keystone_discover_ver,\
                mock.patch(mok_ky_discover_client) as keystone_discover_cli:

            keystone_auth_mock.return_value = True

            keystone_discover_ver.return_value = \
                self.keystone_discovery_version_data
            keystone_discover_cli.return_value = FakeClient()
            keystone_v2_client.return_value = FakeClient()

            keystone_raw_token_mock.return_value = FakeAccess()

            authengine = self.create_authengine(userid=username,
                                                usertype=usertype,
                                                credentials=apikey,
                                                auth_method=auth_method,
                                                datacenter=datacenter,
                                                auth_url=auth_url)

            token = authengine.GetToken(retry=FakeAccess.raise_until)

            FakeAccess.user_data['tenant']['id'] = None
            tenant_id = authengine.AuthTenantId
            self.assertIsNone(tenant_id)

            FakeAccess.user_data['tenant']['id'] = 1
            tenant_id = authengine.AuthTenantId
            self.assertIsNotNone(tenant_id)
            self.assertEqual(tenant_id, FakeAccess.user_data['tenant']['id'])

            FakeAccess.user_data['tenant']['name'] = None
            tenant_name = authengine.AuthTenantName
            self.assertIsNone(tenant_name)

            FakeAccess.user_data['tenant']['name'] = '1'
            tenant_name = authengine.AuthTenantName
            self.assertIsNotNone(tenant_name)
            self.assertEqual(tenant_name,
                             FakeAccess.user_data['tenant']['name'])

            FakeAccess.user_data['user']['id'] = None
            user_id = authengine.AuthUserId
            self.assertIsNone(user_id)

            FakeAccess.user_data['user']['id'] = 1
            user_id = authengine.AuthUserId
            self.assertIsNotNone(user_id)
            self.assertEqual(user_id, FakeAccess.user_data['user']['id'])

            FakeAccess.user_data['user']['name'] = None
            user_name = authengine.AuthUserName
            self.assertIsNone(user_name)

            FakeAccess.user_data['user']['name'] = '1'
            user_name = authengine.AuthUserName
            self.assertIsNotNone(user_name)
            self.assertEqual(user_name, FakeAccess.user_data['user']['name'])

            FakeAccess.user_data['tenant']['id'] = None
            FakeAccess.user_data['tenant']['name'] = None
            FakeAccess.user_data['user']['id'] = None
            FakeAccess.user_data['user']['name'] = None
