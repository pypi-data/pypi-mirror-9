"""
Tests - Deuce Client - Auth - Rackspace Authentication
"""

from unittest import TestCase

import deuceclient.auth
import deuceclient.auth.rackspaceauth as rackspaceauth
import deuceclient.tests.test_auth_openstack as openstacktest


class RackspaceAuthTest(openstacktest.OpenStackAuthTest):

    def create_authengine(self, userid=None, usertype=None,
                          credentials=None, auth_method=None,
                          datacenter=None, auth_url=None):
        return rackspaceauth.RackspaceAuthentication(userid=userid,
                                                     usertype=usertype,
                                                     credentials=credentials,
                                                     auth_method=auth_method,
                                                     datacenter=datacenter,
                                                     auth_url=auth_url)

    def test_get_identity(self):
        main_dc_list = ('us', 'uk', 'lon', 'iad', 'dfw', 'ord')

        for dc in main_dc_list:
            uri = rackspaceauth.get_identity_apihost(dc)
            self.assertEqual(uri,
                             'https://identity.api.rackspacecloud.com/v2.0')

        secondary_dc_list = ('hkg', 'syd')
        for dc in secondary_dc_list:
            uri = rackspaceauth.get_identity_apihost(dc)
            expected_uri = 'https://{0:}.identity.api.rackspacecloud.com/v2.0'.\
                format(dc)
            self.assertEqual(uri, expected_uri)

        with self.assertRaises(deuceclient.auth.AuthenticationError) \
                as auth_error:

            uri = rackspaceauth.get_identity_apihost('bizzaar')

    def test_keystone_management_url_patcher(self):
        main_dc_list = ('us', 'uk', 'lon', 'iad', 'dfw', 'ord')

        for dc in main_dc_list:
            uri = rackspaceauth.RackspaceAuthentication._management_url(
                region_name=dc)
            self.assertEqual(uri,
                             'https://identity.api.rackspacecloud.com/v2.0')

        secondary_dc_list = ('hkg', 'syd')
        for dc in secondary_dc_list:
            uri = rackspaceauth.RackspaceAuthentication._management_url(
                region_name=dc)
            expected_uri = 'https://{0:}.identity.api.rackspacecloud.com/v2.0'.\
                format(dc)
            self.assertEqual(uri, expected_uri)

        with self.assertRaises(deuceclient.auth.AuthenticationError) \
                as auth_error:

            uri = rackspaceauth.RackspaceAuthentication._management_url(
                region_name='bizzaar')

    def test_detect_auth_url(self):

        userid = self.create_userid()
        apikey = self.create_apikey()

        # Neither auth_url nor datacenter are specified
        # At least DC has to be specified
        with self.assertRaises(deuceclient.auth.AuthenticationError) \
                as auth_error:

            authengine = self.create_authengine(userid=userid,
                                                usertype='user_id',
                                                credentials=apikey,
                                                auth_method='apikey',
                                                datacenter=None,
                                                auth_url=None)

        # Auth_url is not specified and DC is unknown
        with self.assertRaises(deuceclient.auth.AuthenticationError) \
                as auth_error:

            authengine = self.create_authengine(userid=userid,
                                                usertype='user_id',
                                                credentials=apikey,
                                                auth_method='apikey',
                                                datacenter='bizzaar',
                                                auth_url=None)

        authengine = self.create_authengine(userid=userid,
                                            usertype='user_id',
                                            credentials=apikey,
                                            auth_method='apikey',
                                            datacenter='us',
                                            auth_url=None)
        self.assertEqual(authengine.authurl,
                         'https://identity.api.rackspacecloud.com/v2.0')
