"""
Tests - Deuce Client - Common - Validation - Instances
"""
import mock
from unittest import TestCase

from stoplight import validate

import deuceclient.api as api
import deuceclient.common.validation_instance as val_instance
import deuceclient.common.errors as errors
from deuceclient.tests import *
from deuceclient.utils import UniformSplitter


class ValidationInstanceTests(TestCase):

    def setUp(self):
        super(ValidationInstanceTests, self).setUp()

        self.project_id = create_project_name()
        self.vault_id = create_vault_name()
        self.block = create_block()
        self.storage_id = create_storage_block()

    def tearDown(self):
        super(ValidationInstanceTests, self).tearDown()

    def test_project_intnace(self):
        project = api.Project(self.project_id)

        @validate(value=val_instance.ProjectInstanceRule)
        def check_project(value):
            return True

        self.assertTrue(check_project(project))

        with self.assertRaises(errors.InvalidProjectInstance):
            check_project(project.project_id)

    def test_vault_instance(self):
        vault = api.Vault(self.project_id, self.vault_id)

        @validate(value=val_instance.VaultInstanceRule)
        def check_vault(value):
            return True

        self.assertTrue(check_vault(vault))

        with self.assertRaises(errors.InvalidVaultInstance):
            check_vault(vault.vault_id)

    def test_block_instance(self):
        block = api.Block(self.project_id, self.vault_id, self.block[0])

        @validate(value=val_instance.BlockInstanceRule)
        def check_block(value):
            return True

        self.assertTrue(check_block(block))

        with self.assertRaises(errors.InvalidBlockInstance):
            check_block(block.block_id)

    def test_file_splitter_instance(self):
        reader = make_reader(100, null_data=True)
        splitter = UniformSplitter(self.project_id, self.vault_id, reader)

        @validate(value=val_instance.FileSplitterInstanceRule)
        def check_splitter(value):
            return True

        self.assertTrue(check_splitter(splitter))

        with self.assertRaises(errors.InvalidFileSplitterType):
            check_splitter(self.project_id)
