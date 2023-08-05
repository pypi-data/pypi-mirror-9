"""
Tests - Deuce Client - API Block
"""
import datetime
import os
from unittest import TestCase

import deuceclient.api as api
import deuceclient.common.errors as errors
import deuceclient.common.validation as val
from deuceclient.tests import *


class BlockTest(TestCase):

    def setUp(self):
        super(BlockTest, self).setUp()

        self.project_id = create_project_name()
        self.vault_id = create_vault_name()
        self.block = create_block()
        self.storage_id = create_storage_block()

    def test_make_block_id(self):
        data = os.urandom(100)

        block_id = api.Block.make_id(data)
        self.assertIsNotNone(block_id)

        block = api.Block(self.project_id,
                          self.vault_id,
                          block_id,
                          data=data)

    def test_create_block_storageid_block_id_None(self):
        with self.assertRaises(ValueError):
            block = api.Block(self.project_id,
                            self.vault_id)

    def test_create_block(self):
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0])
        self.assertEqual(self.project_id,
                         block.project_id)
        self.assertEqual(self.vault_id,
                         block.vault_id)
        self.assertEqual(self.block[0],
                         block.block_id)
        self.assertEqual(0,
                         len(block))
        self.assertIsNone(block.storage_id)
        self.assertIsNone(block.data)
        self.assertIsNone(block.ref_count)
        self.assertIsNone(block.ref_modified)

    def test_create_block_with_data(self):
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0],
                          storage_id=None,
                          data=self.block[1])
        self.assertEqual(self.project_id,
                         block.project_id)
        self.assertEqual(self.vault_id,
                         block.vault_id)
        self.assertEqual(self.block[0],
                         block.block_id)
        self.assertEqual(self.block[2],
                         len(block))
        self.assertIsNone(block.storage_id)
        self.assertEqual(self.block[1],
                         block.data)
        self.assertIsNone(block.ref_count)
        self.assertIsNone(block.ref_modified)

    def test_create_block_with_storage_id(self):
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0],
                          storage_id=self.storage_id,
                          data=self.block[1])
        self.assertEqual(self.project_id,
                         block.project_id)
        self.assertEqual(self.vault_id,
                         block.vault_id)
        self.assertEqual(self.block[0],
                         block.block_id)
        self.assertEqual(self.block[2],
                         len(block))
        self.assertIsNotNone(block.storage_id)
        self.assertEqual(self.storage_id,
                         block.storage_id)
        self.assertEqual(self.block[1],
                         block.data)
        self.assertIsNone(block.ref_count)
        self.assertIsNone(block.ref_modified)

    def test_create_block_with_invalid_storage_id(self):
        storage_id = 'Say, have you seen a wabbit wun by here?'

        with self.assertRaises(errors.InvalidStorageBlocks):
            block = api.Block(self.project_id,
                              self.vault_id,
                              self.block[0],
                              storage_id=storage_id,
                              data=self.block[1])

    def test_create_block_with_ref_count(self):
        ref_count = 5
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0],
                          storage_id=self.storage_id,
                          ref_count=ref_count)
        self.assertEqual(self.project_id,
                         block.project_id)
        self.assertEqual(self.vault_id,
                         block.vault_id)
        self.assertEqual(self.block[0],
                         block.block_id)
        self.assertIsNotNone(block.storage_id)
        self.assertEqual(self.storage_id,
                         block.storage_id)
        self.assertIsNone(block.data)
        self.assertEqual(ref_count, block.ref_count)
        self.assertIsNone(block.ref_modified)

    def test_create_block_with_ref_modified(self):
        ref_modified = int(datetime.datetime.utcnow().timestamp())
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0],
                          storage_id=self.storage_id,
                          ref_modified=ref_modified)
        self.assertEqual(self.project_id,
                         block.project_id)
        self.assertEqual(self.vault_id,
                         block.vault_id)
        self.assertEqual(self.block[0],
                         block.block_id)
        self.assertIsNotNone(block.storage_id)
        self.assertEqual(self.storage_id,
                         block.storage_id)
        self.assertIsNone(block.data)
        self.assertIsNone(block.ref_count)
        self.assertEqual(ref_modified, block.ref_modified)

    def test_update_block_storage_id(self):
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0])

        block.storage_id = self.storage_id
        self.assertEqual(self.storage_id,
                         block.storage_id)

    def test_set_block_type_invalid(self):
        # Only accepted values for block_type are
        # 'storage' and 'metadata'
        with self.assertRaises(ValueError):
            block = api.Block(self.project_id,
                              self.vault_id,
                              storage_id=self.storage_id,
                              block_type='bugs-bunny')

    def test_update_block_storage_id_block_type_storage(self):
        block = api.Block(self.project_id,
                          self.vault_id,
                          storage_id=self.storage_id,
                          block_type='storage')

        with self.assertRaises(ValueError):
            block.storage_id = self.storage_id

    def test_update_block_block_id_block_type_metadata(self):
        block = api.Block(self.project_id,
                          self.vault_id,
                          block_id=self.block[0],
                          block_type='metadata')

        with self.assertRaises(ValueError):
            block.block_id = self.block[0]

    def test_block_block_id_block_type_storage(self):
        # Block cannot be instantiated with block_type
        # set to storage, if storage_id is None
        with self.assertRaises(ValueError):
            block = api.Block(self.project_id,
                              self.vault_id,
                              block_id=self.block[0],
                              block_type='storage')

    def test_block_storage_id_block_type_metadata(self):
        # Block cannot be instantiated with block_type
        # set to metadata, if block_id is None
        with self.assertRaises(ValueError):
            block = api.Block(self.project_id,
                              self.vault_id,
                              storage_id=self.storage_id,
                              block_type='metadata')

    def test_update_block_storage_id_invalid(self):
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0])

        storage_id = 'that wasically wabbit'
        with self.assertRaises(errors.InvalidStorageBlocks):
            block.storage_id = storage_id

    def test_update_block_data(self):
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0])

        self.assertEqual(0,
                         len(block))
        block.data = self.block[1]
        self.assertEqual(self.block[1],
                         block.data)
        self.assertEqual(self.block[2],
                         len(block))

    def test_reset_block_data(self):
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0],
                          data=self.block[1])

        self.assertIsNotNone(block.data)
        self.assertEqual(self.block[1],
                         block.data)
        self.assertEqual(self.block[2],
                         len(block))

        block.data = None

        self.assertIsNone(block.data)
        self.assertNotEqual(self.block[1],
                            block.data)
        self.assertEqual(0,
                         len(block))

    def test_update_ref_count(self):
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0])

        self.assertIsNone(block.ref_count)

        ref_count = 10
        block.ref_count = ref_count

        self.assertIsNotNone(block.ref_count)
        self.assertEqual(ref_count,
                         block.ref_count)

    def test_reset_ref_count(self):
        ref_count = 10
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0],
                          ref_count=ref_count)

        self.assertIsNotNone(block.ref_count)
        self.assertEqual(ref_count,
                         block.ref_count)

        block.ref_count = None

        self.assertIsNone(block.ref_count)
        self.assertNotEqual(ref_count,
                            block.ref_count)

    def test_update_ref_modified(self):
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0])

        self.assertIsNone(block.ref_modified)

        ref_modified = datetime.datetime.utcnow().toordinal()
        block.ref_modified = ref_modified

        self.assertIsNotNone(block.ref_modified)
        self.assertEqual(ref_modified,
                         block.ref_modified)

    def test_reset_ref_modified(self):
        ref_modified = datetime.datetime.utcnow().toordinal()
        block = api.Block(self.project_id,
                          self.vault_id,
                          self.block[0],
                          ref_modified=ref_modified)

        self.assertIsNotNone(block.ref_modified)
        self.assertEqual(ref_modified,
                         block.ref_modified)

        block.ref_modified = None

        self.assertIsNone(block.ref_modified)
        self.assertNotEqual(ref_modified,
                            block.ref_modified)

    def test_modify_block_size(self):
        block_size = 200
        block = api.Block(self.project_id,
                        self.vault_id,
                        self.block[0],
                        data=None,
                        block_size=block_size)

        self.assertEqual(block_size,
                         len(block))

        block.set_block_size(300)

        self.assertNotEqual(block_size,
                            len(block))

    def test_modify_block_orphaned(self):
        block_orphaned = False
        block = api.Block(self.project_id,
                        self.vault_id,
                        self.block[0],
                        block_orphaned=block_orphaned)

        self.assertIsNotNone(block.block_orphaned)
        self.assertEqual(block.block_orphaned,
                         block_orphaned)

        block.block_orphaned = True

        self.assertIsNotNone(block.block_orphaned)
        self.assertTrue(block.block_orphaned)
