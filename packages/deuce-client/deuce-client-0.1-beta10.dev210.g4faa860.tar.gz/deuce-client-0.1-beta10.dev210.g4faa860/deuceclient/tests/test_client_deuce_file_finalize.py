"""
Tests - Deuce Client - Client - Deuce - File - Finalize
"""
import json

import httpretty

import deuceclient.api as api
import deuceclient.client.deuce
from deuceclient.tests import *


class ClientDeuceFileFinalizationTests(ClientTestBase):

    def setUp(self):
        super(ClientDeuceFileFinalizationTests, self).setUp()

        self.client = deuceclient.client.deuce.DeuceClient(self.authenticator,
                                                           self.apihost,
                                                           sslenabled=True)

        self.file_id = create_file()
        self.file_url = get_file_url(self.apihost,
                                     self.vault.vault_id,
                                     self.file_id)

    def tearDown(self):
        super(ClientDeuceFileFinalizationTests, self).tearDown()

    def test_file_finalize_file_not_in_vault(self):

        with self.assertRaises(KeyError):
            self.client.FinalizeFile(self.vault, self.file_id)

    @httpretty.activate
    def test_file_finalize_failure(self):
        self.vault.add_file(self.file_id)

        httpretty.register_uri(httpretty.POST,
                               get_file_url(self.apihost,
                                            self.vault.vault_id,
                                            self.file_id),
                               adding_headers={
                                   'content-type': 'text/plain',
                               },
                               body='[{"error": "mock error"}]',
                               status=409)

        with self.assertRaises(RuntimeError):
            self.client.FinalizeFile(self.vault, self.file_id)

    @httpretty.activate
    def test_file_finalize_success(self):
        self.vault.add_file(self.file_id)

        httpretty.register_uri(httpretty.POST,
                               get_file_url(self.apihost,
                                            self.vault.vault_id,
                                            self.file_id),
                               adding_headers={
                                   'content-type': 'text/plain',
                               },
                               body='mock success',
                               status=200)

        self.client.FinalizeFile(self.vault, self.file_id)
