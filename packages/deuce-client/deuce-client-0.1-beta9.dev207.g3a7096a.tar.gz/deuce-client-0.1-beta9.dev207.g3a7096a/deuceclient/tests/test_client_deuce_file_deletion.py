"""
Tests - Deuce Client - Client - Deuce - File - Deletion
"""
import json

import httpretty

import deuceclient.api as api
import deuceclient.client.deuce
from deuceclient.tests import *


class ClientDeuceFileDeletionTests(ClientTestBase):

    def setUp(self):
        super(ClientDeuceFileDeletionTests, self).setUp()

        self.client = deuceclient.client.deuce.DeuceClient(self.authenticator,
                                                           self.apihost,
                                                           sslenabled=True)

    def tearDown(self):
        super(ClientDeuceFileDeletionTests, self).tearDown()

    @httpretty.activate
    def test_file_deletion(self):
        file_id = create_file()
        file_url = get_file_url(self.apihost, self.vault.vault_id, file_id)

        httpretty.register_uri(httpretty.DELETE,
                               file_url,
                               status=204)

        self.assertTrue(self.client.DeleteFile(self.vault,
                                               file_id))

    @httpretty.activate
    def test_file_deletion_failed(self):
        file_id = create_file()
        file_url = get_file_url(self.apihost, self.vault.vault_id, file_id)

        httpretty.register_uri(httpretty.DELETE,
                               file_url,
                               status=404)

        with self.assertRaises(RuntimeError):
            self.client.DeleteFile(self.vault, file_id)
