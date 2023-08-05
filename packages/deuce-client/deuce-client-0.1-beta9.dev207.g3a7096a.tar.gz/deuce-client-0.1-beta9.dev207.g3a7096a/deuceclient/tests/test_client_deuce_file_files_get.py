"""
Tests - Deuce Client - Client - Deuce - Files - Get
"""
import json
import urllib.parse

import httpretty

import deuceclient.api as api
import deuceclient.client.deuce
from deuceclient.tests import *


@httpretty.activate
class ClientDeuceFileGetFilesTests(ClientTestBase):

    def setUp(self):
        super(ClientDeuceFileGetFilesTests, self).setUp()

        self.client = deuceclient.client.deuce.DeuceClient(self.authenticator,
                                                           self.apihost,
                                                           sslenabled=True)

    def tearDown(self):
        super(ClientDeuceFileGetFilesTests, self).tearDown()

    def test_file_get(self):

        data = [create_file() for _ in range(10)]

        httpretty.register_uri(httpretty.GET,
                               get_files_url(self.apihost,
                                             self.vault.vault_id),
                               body=json.dumps(data),
                               status=200)

        file_list = self.client.ListFiles(self.vault)
        self.assertEqual(file_list, data)
        self.assertIsNone(self.vault.files.marker)

    def test_file_get_with_marker(self):

        data = [create_file() for _ in range(10)]

        httpretty.register_uri(httpretty.GET,
                               get_files_url(self.apihost,
                                             self.vault.vault_id),
                               body=json.dumps(data),
                               status=200)

        file_list = self.client.ListFiles(self.vault, marker=data[0])
        self.assertEqual(file_list, data)
        self.assertIsNone(self.vault.files.marker)

    def test_file_get_with_limit(self):

        data = [create_file() for _ in range(10)]

        httpretty.register_uri(httpretty.GET,
                               get_files_url(self.apihost,
                                             self.vault.vault_id),
                               body=json.dumps(data),
                               status=200)

        file_list = self.client.ListFiles(self.vault, limit=10)
        self.assertEqual(file_list, data)
        self.assertIsNone(self.vault.files.marker)

    def test_file_get_with_marker_and_limit(self):

        data = [create_file() for _ in range(10)]

        httpretty.register_uri(httpretty.GET,
                               get_files_url(self.apihost,
                                             self.vault.vault_id),
                               body=json.dumps(data),
                               status=200)

        file_list = self.client.ListFiles(self.vault,
                                          marker=data[0],
                                          limit=10)
        self.assertEqual(file_list, data)
        self.assertIsNone(self.vault.files.marker)

    def test_file_get_with_marker_more_data(self):

        data = [create_file() for _ in range(10)]
        next_file = create_file()

        url = get_files_url(self.apihost, self.vault.vault_id)
        url_params = urllib.parse.urlencode({'marker': next_file})
        next_batch = '{0}?{1}'.format(url, url_params)
        httpretty.register_uri(httpretty.GET,
                               get_files_url(self.apihost,
                                             self.vault.vault_id),
                               body=json.dumps(data),
                               adding_headers={
                                   'x-next-batch': next_batch
                               },
                               status=200)

        file_list = self.client.ListFiles(self.vault, marker=data[0])
        self.assertEqual(file_list, data)
        self.assertEqual(self.vault.files.marker, next_file)

    def test_file_get(self):
        httpretty.register_uri(httpretty.GET,
                               get_files_url(self.apihost,
                                             self.vault.vault_id),
                               body='mock error',
                               status=404)

        with self.assertRaises(RuntimeError):
            self.client.ListFiles(self.vault)
