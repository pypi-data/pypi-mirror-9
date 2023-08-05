"""
Tests - Deuce Client - Client - Deuce - File - Blocks - Get
"""
import json
import urllib.parse

import httpretty

import deuceclient.api as api
import deuceclient.client.deuce
from deuceclient.tests import *


class ClientDeuceFileGetBlocksTests(ClientTestBase):

    def setUp(self):
        super(ClientDeuceFileGetBlocksTests, self).setUp()

        self.client = deuceclient.client.deuce.DeuceClient(self.authenticator,
                                                           self.apihost,
                                                           sslenabled=True)

    def tearDown(self):
        super(ClientDeuceFileGetBlocksTests, self).tearDown()

    @httpretty.activate
    def test_file_blocks_get(self):
        file_id = create_file()
        self.vault.files[file_id] = api.File(project_id=self.vault.project_id,
                                             vault_id=self.vault.vault_id,
                                             file_id=file_id)

        data = []
        return_data = []

        running_offset = 0
        for block_id, block_data, block_size in create_blocks(5):
            data.append((block_id, running_offset))
            return_data.append(block_id)

            running_offset = running_offset + block_size

        httpretty.register_uri(httpretty.GET,
                               get_file_blocks_url(self.apihost,
                                                   self.vault.vault_id,
                                                   file_id),
                               body=json.dumps(data),
                               status=200)

        block_list, block_next = self.client.GetFileBlockList(self.vault,
                                                              file_id)
        self.assertEqual(return_data,
                         block_list)
        self.assertIsNone(block_next)

    @httpretty.activate
    def test_file_blocks_get_with_next_batch(self):
        file_id = create_file()
        next_block = [block[0] for block in create_blocks(block_count=1)][0]
        self.vault.files[file_id] = api.File(project_id=self.vault.project_id,
                                             vault_id=self.vault.vault_id,
                                             file_id=file_id)

        data = []
        return_data = []

        running_offset = 0
        for block_id, block_data, block_size in create_blocks(5):
            data.append((block_id, running_offset))
            return_data.append(block_id)

            running_offset = running_offset + block_size

        url = get_file_blocks_url(self.apihost, self.vault.vault_id, file_id)
        url_params = urllib.parse.urlencode({'marker': next_block})
        next_batch = '{0}?{1}'.format(url, url_params)
        httpretty.register_uri(httpretty.GET,
                               url,
                               adding_headers={
                                   'x-next-batch': next_batch
                               },
                               body=json.dumps(data),
                               status=200)

        block_list, block_next = self.client.GetFileBlockList(self.vault,
                                                              file_id)
        self.assertEqual(return_data,
                         block_list)
        self.assertIsNotNone(block_next)
        self.assertEqual(block_next, next_block)

    def test_file_blocks_get_bad_vault(self):
        file_id = create_file()
        self.vault.files[file_id] = api.File(project_id=self.vault.project_id,
                                             vault_id=self.vault.vault_id,
                                             file_id=file_id)

        with self.assertRaises(TypeError):
            self.client.GetFileBlockList(self.vault.vault_id, file_id)

    def test_file_blocks_get_bad_fileid(self):
        file_id = create_file()

        with self.assertRaises(KeyError):
            self.client.GetFileBlockList(self.vault, file_id)

    @httpretty.activate
    def test_file_blocks_get_with_marker(self):
        block_id, block_data, block_size = create_block()
        file_id = create_file()
        self.vault.files[file_id] = api.File(project_id=self.vault.project_id,
                                             vault_id=self.vault.vault_id,
                                             file_id=file_id)
        data = []
        return_data = []

        running_offset = 0
        for block_id, block_data, block_size in create_blocks(5):
            data.append((block_id, running_offset))
            return_data.append(block_id)

            running_offset = running_offset + block_size

        httpretty.register_uri(httpretty.GET,
                               get_file_blocks_url(self.apihost,
                                                   self.vault.vault_id,
                                                   file_id),
                               body=json.dumps(data),
                               status=200)

        block_list, block_next = self.client.GetFileBlockList(self.vault,
                                                              file_id,
                                                              marker=block_id)
        self.assertEqual(return_data,
                         block_list)
        self.assertIsNone(block_next)

    @httpretty.activate
    def test_file_blocks_get_with_marker_and_limit(self):
        block_id, block_data, block_size = create_block()
        file_id = create_file()
        self.vault.files[file_id] = api.File(project_id=self.vault.project_id,
                                             vault_id=self.vault.vault_id,
                                             file_id=file_id)
        data = []
        return_data = []

        running_offset = 0
        for block_id, block_data, block_size in create_blocks(5):
            data.append((block_id, running_offset))
            return_data.append(block_id)

            running_offset = running_offset + block_size

        httpretty.register_uri(httpretty.GET,
                               get_file_blocks_url(self.apihost,
                                                   self.vault.vault_id,
                                                   file_id),
                               body=json.dumps(data),
                               status=200)

        block_list, block_next = self.client.GetFileBlockList(self.vault,
                                                              file_id,
                                                              marker=block_id,
                                                              limit=5)
        self.assertEqual(return_data,
                         block_list)
        self.assertIsNone(block_next)

    @httpretty.activate
    def test_file_blocks_get_with_limit_only(self):
        block_id, block_data, block_size = create_block()
        file_id = create_file()
        self.vault.files[file_id] = api.File(project_id=self.vault.project_id,
                                             vault_id=self.vault.vault_id,
                                             file_id=file_id)
        data = []
        return_data = []

        running_offset = 0
        for block_id, block_data, block_size in create_blocks(5):
            data.append((block_id, running_offset))
            return_data.append(block_id)

            running_offset = running_offset + block_size

        httpretty.register_uri(httpretty.GET,
                               get_file_blocks_url(self.apihost,
                                                   self.vault.vault_id,
                                                   file_id),
                               body=json.dumps(data),
                               status=200)

        block_list, block_next = self.client.GetFileBlockList(self.vault,
                                                              file_id,
                                                              limit=5)
        self.assertEqual(return_data,
                         block_list)
        self.assertIsNone(block_next)

    @httpretty.activate
    def test_file_blocks_get_failed(self):
        file_id = create_file()
        self.vault.files[file_id] = api.File(project_id=self.vault.project_id,
                                             vault_id=self.vault.vault_id,
                                             file_id=file_id)
        data = []

        running_offset = 0
        for block_id, block_data, block_size in create_blocks(5):
            data.append((running_offset, block_id))

            running_offset = running_offset + block_size

        httpretty.register_uri(httpretty.GET,
                               get_file_blocks_url(self.apihost,
                                                   self.vault.vault_id,
                                                   file_id),
                               body=json.dumps(data),
                               status=404)

        with self.assertRaises(RuntimeError) as stats_error:
            self.client.GetFileBlockList(self.vault, file_id)
