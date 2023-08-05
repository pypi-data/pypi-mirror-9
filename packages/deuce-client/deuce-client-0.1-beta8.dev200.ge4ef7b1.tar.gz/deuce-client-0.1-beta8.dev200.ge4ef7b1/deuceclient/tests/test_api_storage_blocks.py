"""
Testing - Deuce Client - API Storage Blocks
"""
from unittest import TestCase

import deuceclient.api as api
import deuceclient.common.errors as errors
import deuceclient.common.validation as val
from deuceclient.tests import *


class InvalidStorageBlock(object):

    def __init__(self):
        self._block_type = 'storage'
        self.storage_id = create_storage_block()

    @property
    def block_type(self):
        return self._block_type


class StorageBlocksTest(TestCase):

    def setUp(self):
        super(self.__class__, self).setUp()

        self.project_id = create_project_name()
        self.vault_id = create_vault_name()
        self.storageblock = create_storage_block()

    def test_create_blocks(self):
        blocks = api.StorageBlocks(project_id=self.project_id,
                                  vault_id=self.vault_id)

        self.assertEqual(blocks.project_id, self.project_id)
        self.assertEqual(blocks.vault_id, self.vault_id)

    def test_create_blocks_no_project(self):
        with self.assertRaises(errors.InvalidProject):
            blocks = api.StorageBlocks(vault_id=self.vault_id)

    def test_create_blocks_none_project(self):
        with self.assertRaises(errors.InvalidProject):
            blocks = api.StorageBlocks(project_id=None,
                                       vault_id=self.vault_id)

    def test_create_blocks_no_vault(self):
        with self.assertRaises(errors.InvalidVault):
            blocks = api.StorageBlocks(project_id=self.project_id)

    def test_create_blocks_none_vault(self):
        with self.assertRaises(errors.InvalidVault):
            blocks = api.StorageBlocks(project_id=self.project_id,
                                       vault_id=None)

    def test_set_marker(self):
        blocks = api.StorageBlocks(project_id=self.project_id,
                                   vault_id=self.vault_id)
        self.assertIsNone(blocks.marker)

        marker = create_storage_block()
        blocks.marker = marker
        self.assertIsNotNone(blocks.marker)
        self.assertEqual(blocks.marker,
                         marker)

        blocks.marker = None
        self.assertIsNone(blocks.marker)

    def test_add_block(self):
        block = api.Block(self.project_id,
                        self.vault_id,
                        storage_id=self.storageblock,
                        block_type='storage')

        blocks = api.StorageBlocks(project_id=self.project_id,
                                  vault_id=self.vault_id)
        blocks[block.storage_id] = block

        self.assertEqual(block,
                         blocks[block.storage_id])

    def test_add_invalid_block(self):
        block = api.Block(self.project_id,
                        self.vault_id,
                        storage_id=self.storageblock,
                        block_type='storage')

        blocks = api.StorageBlocks(project_id=self.project_id,
                                  vault_id=self.vault_id)
        with self.assertRaises(errors.InvalidStorageBlocks):
            blocks['alfonso'] = block

        with self.assertRaises(TypeError):
            blocks[block.storage_id] = 'what\'s up doc?'

    def test_add_invalid_block_instance(self):
        block = InvalidStorageBlock()
        blocks = api.StorageBlocks(project_id=self.project_id,
                                  vault_id=self.vault_id)
        with self.assertRaises(TypeError):
            blocks[block.storage_id] = block

    def test_add_block_alternate(self):
        block = api.Block(self.project_id,
                        self.vault_id,
                        storage_id=self.storageblock,
                        block_type='storage')

        blocks = api.StorageBlocks(project_id=self.project_id,
                                  vault_id=self.vault_id)
        blocks.add(block)

        self.assertEqual(block,
                         blocks[block.storage_id])

    def test_add_block_alternate_invalid_block_instance(self):
        block = InvalidStorageBlock()
        blocks = api.StorageBlocks(project_id=self.project_id,
                                  vault_id=self.vault_id)
        with self.assertRaises(TypeError):
            blocks.add(block)

    def test_repr(self):
        blocks = api.StorageBlocks(project_id=self.project_id,
                                  vault_id=self.vault_id)
        serialized_blocks = repr(blocks)

    def test_repr_with_data(self):
        block = api.Block(self.project_id,
                        self.vault_id,
                        storage_id=self.storageblock,
                        block_type='storage')

        blocks = api.StorageBlocks(project_id=self.project_id,
                                  vault_id=self.vault_id)
        blocks[block.storage_id] = block

        serialized_blocks = repr(blocks)

    def test_update(self):
        block = api.Block(self.project_id,
                        self.vault_id,
                        storage_id=self.storageblock,
                        block_type='storage')

        blocks = api.StorageBlocks(project_id=self.project_id,
                                  vault_id=self.vault_id)
        blocks.update({
            block.storage_id: block
        })

        self.assertEqual(block,
                         blocks[block.storage_id])

    def test_update_invalid(self):
        block = api.Block(self.project_id,
                        self.vault_id,
                        storage_id=self.storageblock,
                        block_type='storage')

        blocks = api.StorageBlocks(project_id=self.project_id,
                                  vault_id=self.vault_id)
        with self.assertRaises(TypeError):
            blocks.update({
                self.storageblock: 'be vewy, vewy quiet'
            })

        with self.assertRaises(errors.InvalidStorageBlocks):
            blocks.update({
                'alfonso': block
            })
