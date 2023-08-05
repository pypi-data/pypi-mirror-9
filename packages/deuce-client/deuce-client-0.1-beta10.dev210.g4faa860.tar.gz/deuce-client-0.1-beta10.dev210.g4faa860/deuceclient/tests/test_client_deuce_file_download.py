"""
Tests - Deuce Client - Client - Deuce - File - Download
"""
import json
import os
import tempfile

import httpretty
import mock

import deuceclient.api as api
import deuceclient.client.deuce
from deuceclient.tests import *


class ClientDeuceFileDownloadTests(ClientTestBase):

    def setUp(self):
        super(ClientDeuceFileDownloadTests, self).setUp()
        self.client = deuceclient.client.deuce.DeuceClient(self.authenticator,
                                                           self.apihost,
                                                           sslenabled=True)

    def tearDown(self):
        super(ClientDeuceFileDownloadTests, self).tearDown()

    @httpretty.activate
    def test_file_download_fail_outright(self):
        file_id = create_file()

        httpretty.register_uri(httpretty.GET,
                               get_file_url(self.apihost,
                                            self.vault.vault_id,
                                            file_id),
                               body='mock failure',
                               status=404)

        with self.assertRaises(RuntimeError):
            self.client.DownloadFile(self.vault, file_id, 'blubber')

    @httpretty.activate
    def test_file_download_fail_open_local_file(self):
        file_id = create_file()

        httpretty.register_uri(httpretty.GET,
                               get_file_url(self.apihost,
                                            self.vault.vault_id,
                                            file_id),
                               body=os.urandom(1024),
                               status=200)

        output_file = tempfile.NamedTemporaryFile()

        open_value = mock.mock_open()
        open_value.side_effect = Exception('mock failure')

        with mock.patch('builtins.open', open_value, create=True):
            with self.assertRaises(RuntimeError):
                self.client.DownloadFile(self.vault, file_id, output_file.name)

    @httpretty.activate
    def test_file_download_fail_iter_content(self):
        file_id = create_file()

        httpretty.register_uri(httpretty.GET,
                               get_file_url(self.apihost,
                                            self.vault.vault_id,
                                            file_id),
                               body=os.urandom(2 * 1024 * 1024),
                               status=200)

        output_file = tempfile.NamedTemporaryFile()

        with mock.patch('requests.Response.iter_content') as mok_request:
            mok_request.side_effect = Exception('mock failure')

            with self.assertRaises(RuntimeError):
                self.client.DownloadFile(self.vault, file_id, output_file.name)

    @httpretty.activate
    def test_file_download_success(self):
        file_id = create_file()

        httpretty.register_uri(httpretty.GET,
                               get_file_url(self.apihost,
                                            self.vault.vault_id,
                                            file_id),
                               body=os.urandom(2 * 1024 * 1024),
                               status=200)

        output_file = tempfile.NamedTemporaryFile()
        self.assertEqual(True,
                         self.client.DownloadFile(self.vault,
                                                  file_id,
                                                  output_file.name))
