"""
Tests - Deuce Client - API - Vault - Serialize
"""
from unittest import TestCase

import deuceclient.api as api
import deuceclient.common.errors as errors
import deuceclient.common.validation as val
from deuceclient.tests import *


class VaultTest(VaultTestBase):

    def setUp(self):
        super(VaultTest, self).setUp()

    def tearDown(self):
        super(VaultTest, self).tearDown()

    def test_json_serialize_block(self):
        block_info = create_block()
        block = api.Block(self.project_id,
                          self.vault_id,
                          block_id=block_info[0],
                          data=block_info[1],
                          block_size=block_info[2])

        json_data = block.to_json()

        new_block = api.Block.from_json(json_data)

        self.check_block_instance(block, new_block)

    def test_json_serialize_file(self):
        a_file = api.File(self.project_id,
                          self.vault_id,
                          create_file())
        json_data = a_file.to_json()

        new_file = api.File.from_json(json_data)

        self.check_file_instance(a_file, new_file)

    def test_json_serialize_blocks(self):
        blocks = api.Blocks(self.project_id,
                            self.vault_id)
        blocks.update({
            block[0]: api.Block(self.project_id,
                                self.vault_id,
                                block_id=block[0],
                                data=block[1],
                                block_size=block[2])
            for block in create_blocks(block_count=10)
        })

        json_data = blocks.to_json()

        new_blocks = api.Blocks.from_json(json_data)

        self.check_blocks(blocks, new_blocks)

    def test_json_serialize_storage_blocks(self):
        storageblocks = api.StorageBlocks(self.project_id,
                                          self.vault_id)
        json_data = storageblocks.to_json()

        new_storageblocks = api.StorageBlocks.from_json(json_data)

        self.check_blocks(storageblocks, new_storageblocks)

    def test_json_serialize_files_blocks(self):
        files = api.Files(self.project_id,
                          self.vault_id)
        files.update({
            file_id: api.File(self.project_id,
                              self.vault_id,
                              file_id)
            for file_id in [create_file() for _ in range(10)]
        })

        json_data = files.to_json()

        new_files = api.Files.from_json(json_data)

        self.check_files(files, new_files)

    def test_json_serialize(self):
        vault = api.Vault(self.project_id,
                          self.vault_id)

        json_data = vault.to_json()

        new_vault = api.Vault.from_json(json_data)
        self.check_vault(vault, new_vault)

    def test_json_serialize_with_data(self):
        vault = api.Vault(self.project_id,
                          self.vault_id)

        vault.blocks.update({
            block[0]: api.Block(self.project_id,
                                self.vault_id,
                                block_id=block[0],
                                data=block[1],
                                block_size=block[2])
            for block in create_blocks(block_count=10)
        })
        vault.files.update({
            file_id: api.File(self.project_id,
                              self.vault_id,
                              file_id)
            for file_id in [create_file() for _ in range(10)]
        })

        json_data = vault.to_json()

        new_vault = api.Vault.from_json(json_data)

        self.check_vault(vault, new_vault)
