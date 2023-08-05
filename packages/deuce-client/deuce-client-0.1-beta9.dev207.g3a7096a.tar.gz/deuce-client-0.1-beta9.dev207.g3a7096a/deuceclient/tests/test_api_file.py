"""
Tests - Deuce Client - API File
"""
from unittest import TestCase

import deuceclient.api as api
import deuceclient.common.errors as errors
import deuceclient.common.validation as val
from deuceclient.tests import *
from deuceclient.utils import UniformSplitter


class FileTest(TestCase):

    def setUp(self):
        super(FileTest, self).setUp()

        self.project_id = create_project_name()
        self.vault_id = create_vault_name()
        self.file_id = create_file()
        self.block_data = [
            (create_block(), create_storage_block()) for x in range(10)
        ]

    def test_create_file(self):
        a_file = api.File(self.project_id, self.vault_id, self.file_id)

        self.assertEqual(a_file.project_id, self.project_id)
        self.assertEqual(a_file.vault_id, self.vault_id)
        self.assertEqual(a_file.file_id, self.file_id)
        self.assertEqual(a_file.offsets, {})
        self.assertEqual(a_file.blocks, {})
        self.assertIsNone(a_file.url)

    def test_create_file_with_url(self):
        test_url = 'magic.example.com/open/sesame'
        a_file = api.File(self.project_id,
                          self.vault_id,
                          self.file_id,
                          url=test_url)

        self.assertEqual(a_file.project_id, self.project_id)
        self.assertEqual(a_file.vault_id, self.vault_id)
        self.assertEqual(a_file.file_id, self.file_id)
        self.assertEqual(a_file.offsets, {})
        self.assertEqual(a_file.blocks, {})
        self.assertEqual(a_file.url, test_url)
        self.assertEqual(len(a_file), 0)

    def test_create_file_no_file_id(self):
        a_file = api.File(self.project_id, self.vault_id)

        self.assertEqual(a_file.project_id, self.project_id)
        self.assertEqual(a_file.vault_id, self.vault_id)
        self.assertIsNone(a_file.file_id)
        self.assertEqual(a_file.offsets, {})
        self.assertEqual(a_file.blocks, {})
        self.assertIsNone(a_file.url)

    def test_create_file_no_file_id_alternate(self):
        a_file = api.File(self.project_id, self.vault_id, file_id=None)

        self.assertEqual(a_file.project_id, self.project_id)
        self.assertEqual(a_file.vault_id, self.vault_id)
        self.assertIsNone(a_file.file_id)
        self.assertEqual(a_file.offsets, {})
        self.assertEqual(a_file.blocks, {})
        self.assertIsNone(a_file.url)

    def test_create_file_update_file_id(self):
        a_file = api.File(self.project_id, self.vault_id)

        self.assertEqual(a_file.project_id, self.project_id)
        self.assertEqual(a_file.vault_id, self.vault_id)
        self.assertIsNone(a_file.file_id)
        self.assertEqual(a_file.offsets, {})
        self.assertEqual(a_file.blocks, {})

        a_file.file_id = self.file_id
        self.assertEqual(a_file.file_id, self.file_id)

    def test_assign_block(self):
        a_file = api.File(self.project_id, self.vault_id, self.file_id)

        self.assertEqual(a_file.project_id, self.project_id)
        self.assertEqual(a_file.vault_id, self.vault_id)
        self.assertEqual(a_file.file_id, self.file_id)
        self.assertEqual(a_file.offsets, {})
        self.assertEqual(a_file.blocks, {})
        self.assertEqual(len(a_file), 0)

        last_offset = 0
        offset = 0
        offsets = {}
        for block_data in self.block_data:
            sha1, data, size = block_data[0]
            block = api.Block(self.project_id, self.vault_id, sha1, data=data)
            a_file.add_block(block)
            a_file.add_block(block)
            a_file.assign_block(sha1, offset)
            offsets[offset] = sha1
            last_offset = offset
            offset = offset + size
            self.assertEqual(len(a_file), offset)

        self.assertEqual(len(offsets), len(self.block_data))
        self.assertEqual(len(offsets), len(a_file.offsets))

        for k, v in offsets.items():
            self.assertEqual(a_file.get_block_for_offset(k), v)

        # Remove the last block, thus shortening the file but also
        # failing to update maximum offset in the process so len(a_file)
        # should fail on the key error
        del a_file.blocks[a_file.get_block_for_offset(last_offset)]
        del a_file.offsets[str(last_offset)]

        self.assertEqual(a_file._File__properties['maximum_offset'],
                         len(a_file))

    def test_get_block_offsets(self):
        a_file = api.File(self.project_id, self.vault_id, self.file_id)

        self.assertEqual(a_file.project_id, self.project_id)
        self.assertEqual(a_file.vault_id, self.vault_id)
        self.assertEqual(a_file.file_id, self.file_id)
        self.assertEqual(a_file.offsets, {})
        self.assertEqual(a_file.blocks, {})

        offset = 0
        offsets = {}
        for block_data in self.block_data:
            sha1, data, size = block_data[0]
            block = api.Block(self.project_id, self.vault_id, sha1, data=data)
            a_file.blocks[sha1] = block
            a_file.assign_block(sha1, offset)
            offsets[offset] = sha1

        ub_sha1, ub_data, ub_size = create_block()
        self.assertEqual(a_file.get_offsets_for_block(ub_sha1), [])

        for k, v in offsets.items():
            x = [k]
            self.assertEqual(a_file.get_offsets_for_block(v), x)

    def test_invalid_offsets(self):
        a_file = api.File(self.project_id, self.vault_id, self.file_id)
        sha1, data, size = self.block_data[0][0]

        with self.assertRaises(errors.ParameterConstraintError):
            a_file.assign_block(sha1, 'howdy')

        with self.assertRaises(errors.ParameterConstraintError):
            a_file.assign_block(sha1, -1)

    def test_assign_from_data_source_bad_splitter(self):
        a_file = api.File(self.project_id, self.vault_id, self.file_id)
        with self.assertRaises(errors.InvalidFileSplitterType):
            a_file.assign_from_data_source(self.project_id,
                                           append=False,
                                           count=1)

    def test_assign_from_data_source(self):
        a_file = api.File(self.project_id, self.vault_id, self.file_id)
        splitter = UniformSplitter(self.project_id,
                                   self.vault_id,
                                   make_reader(11 * 1024 * 1024))

        a_file.assign_from_data_source(splitter,
                                       append=False,
                                       count=1)
        self.assertEqual(len(a_file), (1 * splitter.chunk_size))

    def test_assign_from_data_source_no_append(self):
        a_file = api.File(self.project_id, self.vault_id, self.file_id)
        splitter = UniformSplitter(self.project_id,
                                   self.vault_id,
                                   make_reader(11 * 1024 * 1024))

        a_file.assign_from_data_source(splitter,
                                       append=False,
                                       count=1)
        self.assertEqual(len(a_file), (1 * splitter.chunk_size))

        with self.assertRaises(errors.InvalidContentError):
            a_file.assign_from_data_source(splitter,
                                           append=False,
                                           count=1)

    def test_assign_from_data_source_with_append(self):
        a_file = api.File(self.project_id, self.vault_id, self.file_id)
        splitter = UniformSplitter(self.project_id,
                                   self.vault_id,
                                   make_reader(11 * 1024 * 1024))

        a_file.assign_from_data_source(splitter,
                                       append=False,
                                       count=1)
        self.assertEqual(len(a_file), (1 * splitter.chunk_size))

        a_file.assign_from_data_source(splitter,
                                       append=True,
                                       count=1)

        self.assertEqual(len(a_file), (2 * splitter.chunk_size))
