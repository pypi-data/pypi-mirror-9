"""
Tests - Deuce Client - API Files
"""
from unittest import TestCase

import deuceclient.api as api
import deuceclient.common.errors as errors
import deuceclient.common.validation as val
from deuceclient.tests import *


class FileTest(TestCase):

    def setUp(self):
        super(FileTest, self).setUp()

        self.project_id = create_project_name()
        self.vault_id = create_vault_name()
        self.file_id = create_file()

    def test_create_files(self):
        files = api.Files(project_id=self.project_id,
                          vault_id=self.vault_id)
        self.assertEqual(files.project_id,
                         self.project_id)
        self.assertEqual(files.vault_id,
                         self.vault_id)

    def test_create_blocks_no_project(self):
        with self.assertRaises(errors.InvalidProject):
            blocks = api.Files(vault_id=self.vault_id)

    def test_create_blocks_none_project(self):
        with self.assertRaises(errors.InvalidProject):
            blocks = api.Files(project_id=None,
                               vault_id=self.vault_id)

    def test_create_blocks_no_vault(self):
        with self.assertRaises(errors.InvalidVault):
            blocks = api.Files(project_id=self.project_id)

    def test_create_blocks_none_vault(self):
        with self.assertRaises(errors.InvalidVault):
            blocks = api.Files(project_id=self.project_id,
                               vault_id=None)

    def test_set_marker(self):
        files = api.Files(project_id=self.project_id,
                          vault_id=self.vault_id)
        self.assertIsNone(files.marker)

        files.marker = self.file_id
        self.assertIsNotNone(files.marker)
        self.assertEqual(files.marker,
                         self.file_id)

        files.marker = None
        self.assertIsNone(files.marker)

    def test_add_file(self):
        a_file = api.File(self.project_id, self.vault_id, self.file_id)

        files = api.Files(project_id=self.project_id,
                          vault_id=self.vault_id)
        files[a_file.file_id] = a_file

        self.assertEqual(a_file, files[a_file.file_id])

    def test_add_invalid_file(self):
        a_file = api.File(self.project_id, self.vault_id, self.file_id)

        files = api.Files(project_id=self.project_id,
                          vault_id=self.vault_id)

        with self.assertRaises(errors.InvalidFiles):
            files['jessie'] = a_file

        with self.assertRaises(TypeError):
            files[a_file.file_id] = 'james'

    def test_repr(self):
        files = api.Files(project_id=self.project_id,
                          vault_id=self.vault_id)

        serialized_files = repr(files)

    def test_repr_with_data(self):
        a_file = api.File(self.project_id, self.vault_id, self.file_id)

        files = api.Files(project_id=self.project_id,
                          vault_id=self.vault_id)
        files[a_file.file_id] = a_file

        serialized_files = repr(files)

    def test_update(self):
        a_file = api.File(self.project_id, self.vault_id, self.file_id)

        files = api.Files(project_id=self.project_id,
                          vault_id=self.vault_id)
        files.update({
            a_file.file_id: a_file
        })

        self.assertEqual(a_file, files[a_file.file_id])

    def test_update_invalid_file(self):
        a_file = api.File(self.project_id, self.vault_id, self.file_id)

        files = api.Files(project_id=self.project_id,
                          vault_id=self.vault_id)

        with self.assertRaises(errors.InvalidFiles):
            files.update({
                'jessie': a_file
            })

        with self.assertRaises(TypeError):
            files.update({
                a_file.file_id: 'james'
            })
