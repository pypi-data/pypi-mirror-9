"""
Tests - Deuce Client - Client - Deuce - File - Assign Blocks
"""
import json

import httpretty

import deuceclient.api as api
import deuceclient.client.deuce
from deuceclient.tests import *


class ClientDeuceFileTests(ClientTestBase):

    def setUp(self):
        super(ClientDeuceFileTests, self).setUp()
        self.client = deuceclient.client.deuce.DeuceClient(self.authenticator,
                                                           self.apihost,
                                                           sslenabled=True)

    def tearDown(self):
        super(ClientDeuceFileTests, self).tearDown()

    @httpretty.activate
    def test_file_assign_blocks(self):
        file_id = create_file()
        self.vault.files[file_id] = api.File(project_id=self.vault.project_id,
                                             vault_id=self.vault.vault_id,
                                             file_id=file_id)

        block_list = []

        running_offset = 0
        for block_id, block_data, block_size in \
                create_blocks(5):
            self.vault.files[file_id].offsets[str(running_offset)] = block_id

            block_list.append((block_id, running_offset))

            running_offset = running_offset + block_size

        data = ['status']

        httpretty.register_uri(httpretty.POST,
                               get_file_blocks_url(self.apihost,
                                                   self.vault.vault_id,
                                                   file_id),
                               body=json.dumps(data),
                               status=200)

        self.assertEqual(data,
                         self.client.AssignBlocksToFile(self.vault,
                                                        file_id,
                                                        block_list))

    @httpretty.activate
    def test_file_assign_blocks_alternate(self):
        file_id = create_file()
        self.vault.files[file_id] = api.File(project_id=self.vault.project_id,
                                             vault_id=self.vault.vault_id,
                                             file_id=file_id)

        running_offset = 0
        for block_id, block_data, block_size in \
                create_blocks(5):
            self.vault.files[file_id].offsets[str(running_offset)] = block_id

            running_offset = running_offset + block_size

        data = ['status']

        httpretty.register_uri(httpretty.POST,
                               get_file_blocks_url(self.apihost,
                                                   self.vault.vault_id,
                                                   file_id),
                               body=json.dumps(data),
                               status=200)

        self.assertEqual(data,
                         self.client.AssignBlocksToFile(self.vault,
                                                        file_id))

    def test_file_assign_blocks_bad_vault(self):
        file_id = create_file()
        self.vault.files[file_id] = api.File(project_id=self.vault.project_id,
                                             vault_id=self.vault.vault_id,
                                             file_id=file_id)

        block_list = []

        with self.assertRaises(TypeError):
            self.client.AssignBlocksToFile(self.vault.vault_id,
                                           file_id,
                                           block_list)

    def test_file_assign_blocks_bad_fileid(self):
        block_list = []
        file_id = create_file().encode()

        with self.assertRaises(TypeError):
            self.client.AssignBlocksToFile(self.vault,
                                           file_id,
                                           block_list)

    def test_file_assign_blocks_fileid_not_in_vault(self):
        file_id = create_file()

        block_list = []

        with self.assertRaises(KeyError):
            self.client.AssignBlocksToFile(self.vault,
                                           file_id,
                                           block_list)

    def test_file_assign_blocks_bad_blocklist(self):
        file_id = create_file()
        self.vault.files[file_id] = api.File(project_id=self.vault.project_id,
                                             vault_id=self.vault.vault_id,
                                             file_id=file_id)

        block_list = []

        with self.assertRaises(ValueError):
            self.client.AssignBlocksToFile(self.vault,
                                           file_id,
                                           block_list)

    @httpretty.activate
    def test_file_assign_blocks_not_in_files_offsetlist(self):
        file_id = create_file()
        self.vault.files[file_id] = api.File(project_id=self.vault.project_id,
                                             vault_id=self.vault.vault_id,
                                             file_id=file_id)

        block_list = []

        running_offset = 0
        for block_id, block_data, block_size in \
                create_blocks(5):

            block_list.append((block_id, running_offset))

            running_offset = running_offset + block_size

        with self.assertRaises(KeyError):
            self.client.AssignBlocksToFile(self.vault,
                                           file_id,
                                           block_list)

    @httpretty.activate
    def test_file_assign_blocks_files_offsetlist_not_matching(self):
        file_id = create_file()
        self.vault.files[file_id] = api.File(project_id=self.vault.project_id,
                                             vault_id=self.vault.vault_id,
                                             file_id=file_id)

        block_list = []

        running_offset = 0
        for block_id, block_data, block_size in \
                create_blocks(5):
            block_id2, block_data2, block_size2 = create_block()

            self.vault.files[file_id].offsets[str(running_offset)] = block_id2

            block_list.append((block_id, running_offset))

            running_offset = running_offset + block_size

        with self.assertRaises(ValueError):
            self.client.AssignBlocksToFile(self.vault,
                                           file_id,
                                           block_list)

    @httpretty.activate
    def test_file_assign_blocks_no_blocklist_no_offsets(self):
        file_id = create_file()
        self.vault.files[file_id] = api.File(project_id=self.vault.project_id,
                                             vault_id=self.vault.vault_id,
                                             file_id=file_id)

        running_offset = 0
        for block_id, block_data, block_size in \
                create_blocks(5):

            running_offset = running_offset + block_size

        with self.assertRaises(ValueError):
            self.client.AssignBlocksToFile(self.vault,
                                           file_id)

    @httpretty.activate
    def test_file_assign_blocks_failed(self):
        file_id = create_file()
        self.vault.files[file_id] = api.File(project_id=self.vault.project_id,
                                             vault_id=self.vault.vault_id,
                                             file_id=file_id)

        block_list = []

        running_offset = 0
        for block_id, block_data, block_size in create_blocks(5):
            self.vault.files[file_id].offsets[str(running_offset)] = block_id

            block_list.append((block_id, running_offset))

            running_offset = running_offset + block_size

        httpretty.register_uri(httpretty.POST,
                               get_file_blocks_url(self.apihost,
                                                   self.vault.vault_id,
                                                   file_id),
                               content_type='text/plain',
                               body="mock failure",
                               status=404)

        with self.assertRaises(RuntimeError) as stats_error:
            self.client.AssignBlocksToFile(self.vault, file_id, block_list)
