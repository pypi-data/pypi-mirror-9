"""
Tests - Deuce Client - API - Vault
"""
from unittest import TestCase

import deuceclient.api as api
import deuceclient.common.errors as errors
import deuceclient.common.validation as val
from deuceclient.tests import *


class VaultTest(TestCase):

    def setUp(self):
        super(VaultTest, self).setUp()

        self.vault_id = create_vault_name()
        self.project_id = create_project_name()

    def test_vault_creation(self):
        vault = api.Vault(self.project_id, self.vault_id)

        self.assertEqual(vault.vault_id, self.vault_id)
        self.assertEqual(vault.project_id, self.project_id)
        self.assertEqual(vault.status, 'unknown')
        self.assertIsNone(vault.statistics)
        self.assertEqual(vault.blocks,
                         api.Blocks(self.project_id, self.vault_id))
        self.assertEqual(vault.files,
                         api.Files(self.project_id, self.vault_id))

    def test_vault_invalid_project(self):

        with self.assertRaises(errors.InvalidProject):
            vault = api.Vault(self.project_id + '$', self.vault_id)

    def test_vault_invalid_name(self):
        with self.assertRaises(errors.InvalidVault):
            vault = api.Vault(self.project_id, self.vault_id + '$')

        # Build project name that is too long
        x = self.vault_id
        while len(x) < (val.VAULT_ID_MAX_LEN + 1):
            x = '{0}_{1}'.format(x, self.vault_id)

        with self.assertRaises(errors.InvalidVault):
            vault = api.Vault(self.project_id, x)

    def test_vault_status_values(self):

        positive_cases = [
            (None, 'unknown'),
            ('unknown', 'unknown'),
            ('created', 'created'),
            ('deleted', 'deleted'),
            ('valid', 'valid'),
            ('invalid', 'invalid')
        ]

        negative_cases = [
            '0123',
            1, 5, 6,
            'a', 'b', 'c'
        ]

        vault = api.Vault(self.project_id, self.vault_id)

        for case in positive_cases:
            vault.status = case[0]
            self.assertEqual(vault.status, case[1])

        for case in negative_cases:
            with self.assertRaises(ValueError):
                vault.status = case

    def test_vault_statistics(self):

        statistic = 5.0

        vault = api.Vault(self.project_id, self.vault_id)

        vault.statistics = statistic

        self.assertEqual(statistic, vault.statistics)

    def test_add_file(self):

        file_id = create_file()

        vault = api.Vault(self.project_id, self.vault_id)

        vault.add_file(file_id)

    def test_add_file_failure(self):

        file_id = 'wax-on-wax-off'

        vault = api.Vault(self.project_id, self.vault_id)

        with self.assertRaises(errors.InvalidFiles):
            vault.add_file(file_id)
