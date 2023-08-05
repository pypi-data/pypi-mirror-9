"""
Tests - Deuce Client - API - V1 URLs
"""
import hashlib
import json
import os
import random
from unittest import TestCase
import uuid

import httpretty
import mock

import deuceclient.api as api
import deuceclient.tests as baseline


class DeuceClientV1ApiSupportTests(TestCase):

    def setUp(self):
        super(DeuceClientV1ApiSupportTests, self).setUp()

        self.vault_name = baseline.create_vault_name()
        self.file_name = baseline.create_file()
        self.block = baseline.create_block()
        self.block_id = self.block[0]
        self.storage_block_id = baseline.create_storage_block()

    def test_v1_base_url(self):
        self.assertEqual(baseline.get_base_path(),
                         api.v1.get_base_path())

    def test_v1_vault_path(self):
        path = baseline.get_vault_path(self.vault_name)
        self.assertEqual(path,
                         api.v1.get_vault_path(self.vault_name))

    def test_v1_files_path(self):
        path = baseline.get_files_path(self.vault_name)
        self.assertEqual(path,
                         api.v1.get_files_path(self.vault_name))

    def test_v1_file_path(self):
        path = baseline.get_file_path(self.vault_name, self.file_name)
        self.assertEqual(path,
                         api.v1.get_file_path(self.vault_name, self.file_name))

    def test_v1_fileblocks_path(self):
        path = baseline.get_fileblocks_path(self.vault_name, self.file_name)
        self.assertEqual(path,
                         api.v1.get_fileblocks_path(self.vault_name,
                                                    self.file_name))

    def test_v1_blocks_path(self):
        path = baseline.get_blocks_path(self.vault_name)
        self.assertEqual(path,
                         api.v1.get_blocks_path(self.vault_name))

    def test_v1_block_path(self):
        path = baseline.get_block_path(self.vault_name, self.block_id)
        self.assertEqual(path,
                         api.v1.get_block_path(self.vault_name, self.block_id))

    def test_v1_storage_path(self):
        path = baseline.get_storage_path(self.vault_name)
        self.assertEqual(path,
                         api.v1.get_storage_path(self.vault_name))

    def test_v1_storage_blocks_path(self):
        path = baseline.get_storage_blocks_path(self.vault_name)
        self.assertEqual(path,
                         api.v1.get_storage_blocks_path(self.vault_name))

    def test_v1_storage_block_path(self):
        path = baseline.get_storage_block_path(self.vault_name,
                                               self.storage_block_id)
        self.assertEqual(path,
                         api.v1.get_storage_block_path(self.vault_name,
                                                   self.storage_block_id))
