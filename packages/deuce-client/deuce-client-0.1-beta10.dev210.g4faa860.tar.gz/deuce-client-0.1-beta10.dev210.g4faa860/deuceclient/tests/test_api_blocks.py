"""
Tests - Deuce Client - API Blocks
"""
from unittest import TestCase

import deuceclient.api as api
import deuceclient.common.errors as errors
import deuceclient.common.validation as val
from deuceclient.tests import *


class InvalidMetadataBlock(object):

    def __init__(self):
        self._block_type = 'metadata'
        self.block_id = create_block()[0]

    @property
    def block_type(self):
        return self._block_type


class BlocksTest(TestCase):

    def setUp(self):
        super(BlocksTest, self).setUp()

        self.project_id = create_project_name()
        self.vault_id = create_vault_name()
        self.block = create_block()

    def test_create_blocks(self):
        blocks = api.Blocks(project_id=self.project_id,
                            vault_id=self.vault_id)
        self.assertEqual(blocks.project_id,
                         self.project_id)
        self.assertEqual(blocks.vault_id,
                         self.vault_id)

    def test_create_blocks_no_project(self):
        with self.assertRaises(errors.InvalidProject):
            blocks = api.Blocks(vault_id=self.vault_id)

    def test_create_blocks_none_project(self):
        with self.assertRaises(errors.InvalidProject):
            blocks = api.Blocks(project_id=None,
                                vault_id=self.vault_id)

    def test_create_blocks_no_vault(self):
        with self.assertRaises(errors.InvalidVault):
            blocks = api.Blocks(project_id=self.project_id)

    def test_create_blocks_none_vault(self):
        with self.assertRaises(errors.InvalidVault):
            blocks = api.Blocks(project_id=self.project_id,
                                vault_id=None)

    def test_set_marker(self):
        blocks = api.Blocks(project_id=self.project_id,
                            vault_id=self.vault_id)
        self.assertIsNone(blocks.marker)

        blocks.marker = self.block[0]
        self.assertIsNotNone(blocks.marker)
        self.assertEqual(blocks.marker,
                         self.block[0])

        blocks.marker = None
        self.assertIsNone(blocks.marker)

    def test_add_block(self):
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0])

        blocks = api.Blocks(project_id=self.project_id,
                            vault_id=self.vault_id)
        blocks[block.block_id] = block

        self.assertEqual(block,
                         blocks[block.block_id])

    def test_add_invalid_block(self):
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0])

        blocks = api.Blocks(project_id=self.project_id,
                            vault_id=self.vault_id)
        with self.assertRaises(errors.InvalidBlocks):
            blocks['alfonso'] = block

        with self.assertRaises(TypeError):
            blocks[block.block_id] = 'what\'s up doc?'

    def test_add_invalid_block_instance(self):
        block = InvalidMetadataBlock()
        blocks = api.Blocks(project_id=self.project_id,
                            vault_id=self.vault_id)
        with self.assertRaises(TypeError):
            blocks[block.block_id] = block

    def test_add_block_alternate(self):
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0])

        blocks = api.Blocks(project_id=self.project_id,
                            vault_id=self.vault_id)
        blocks.add(block)

        self.assertEqual(block,
                         blocks[block.block_id])

    def test_add_block_alternate_invalid_block_instance(self):
        block = InvalidMetadataBlock()
        blocks = api.Blocks(project_id=self.project_id,
                            vault_id=self.vault_id)
        with self.assertRaises(TypeError):
            blocks.add(block)

    def test_repr(self):
        blocks = api.Blocks(project_id=self.project_id,
                            vault_id=self.vault_id)

        serialized_blocks = repr(blocks)

    def test_repr_with_data(self):
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0])

        blocks = api.Blocks(project_id=self.project_id,
                            vault_id=self.vault_id)
        blocks[block.block_id] = block

        serialized_blocks = repr(blocks)

    def test_update(self):
        block = api.Block(self.project_id,
                          self.vault_id,
                         self.block[0])

        blocks = api.Blocks(project_id=self.project_id,
                            vault_id=self.vault_id)
        blocks.update({
            block.block_id: block
        })

        self.assertEqual(block,
                         blocks[block.block_id])

    def test_update_invalid(self):
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0])

        blocks = api.Blocks(project_id=self.project_id,
                            vault_id=self.vault_id)
        with self.assertRaises(TypeError):
            blocks.update({
                self.block[0]: 'be vewy, vewy quiet'
            })

        with self.assertRaises(errors.InvalidBlocks):
            blocks.update({
                'alfonso': block
            })
