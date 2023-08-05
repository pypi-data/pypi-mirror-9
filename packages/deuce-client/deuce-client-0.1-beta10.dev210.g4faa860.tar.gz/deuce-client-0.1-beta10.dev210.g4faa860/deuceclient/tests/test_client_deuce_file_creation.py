"""
Tests - Deuce Client - Client - Deuce - File - Creation
"""
import json

import httpretty

import deuceclient.api as api
import deuceclient.client.deuce
from deuceclient.tests import *


class ClientDeuceFileCreationTests(ClientTestBase):

    def setUp(self):
        super(ClientDeuceFileCreationTests, self).setUp()

        self.client = deuceclient.client.deuce.DeuceClient(self.authenticator,
                                                           self.apihost,
                                                           sslenabled=True)

    def tearDown(self):
        super(ClientDeuceFileCreationTests, self).tearDown()

    @httpretty.activate
    def test_file_creation(self):
        file_id = create_file()
        file_url = get_file_url(self.apihost, self.vault.vault_id, file_id)

        httpretty.register_uri(httpretty.POST,
                               get_files_url(self.apihost,
                                             self.vault.vault_id),
                               adding_headers={
                                   'location': file_url,
                                   'x-file-id': file_id
                               },
                               status=201)

        file_id = self.client.CreateFile(self.vault)
        self.assertIn(file_id, self.vault.files)
        self.assertEqual(file_url, self.vault.files[file_id].url)

    def test_file_creation_bad_vault(self):
        with self.assertRaises(TypeError):
            self.client.CreateFile(self.vault.vault_id)

    @httpretty.activate
    def test_file_creation_missing_location_header(self):
        file_id = create_file()
        file_url = get_file_url(self.apihost, self.vault.vault_id, file_id)

        httpretty.register_uri(httpretty.POST,
                               get_files_url(self.apihost,
                                             self.vault.vault_id),
                               status=201)

        with self.assertRaises(KeyError) as creation_error:
            self.client.CreateFile(self.vault)

    @httpretty.activate
    def test_file_creation_failed(self):
        file_id = create_file()
        file_url = get_file_url(self.apihost, self.vault.vault_id, file_id)

        httpretty.register_uri(httpretty.POST,
                               get_files_url(self.apihost,
                                             self.vault.vault_id),
                               status=404)

        with self.assertRaises(RuntimeError) as creation_error:
            self.client.CreateFile(self.vault)
