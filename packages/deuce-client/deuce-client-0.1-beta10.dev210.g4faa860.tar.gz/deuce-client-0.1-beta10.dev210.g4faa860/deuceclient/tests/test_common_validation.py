"""
Tests - Deuce Client - Common - Validation
"""
import mock
from unittest import TestCase

from stoplight import validate

import deuceclient.api as api
import deuceclient.common.validation as v
import deuceclient.common.errors as errors
from deuceclient.tests import *


class TestRulesBase(TestCase):

    def cases_with_none_okay(self):

        positive_cases = self.__class__.positive_cases[:]
        positive_cases.append(None)

        negative_cases = self.__class__.negative_cases[:]
        while negative_cases.count(None):
            negative_cases.remove(None)
        while negative_cases.count(''):
            negative_cases.remove('')

        return (positive_cases, negative_cases)

    def iterable_cases(self):

        positive_cases = self.__class__.positive_cases[:]
        while positive_cases.count(None):
            positive_cases.remove(None)
        while positive_cases.count(''):
            positive_cases.remove('')

        negative_cases = self.__class__.negative_cases[:]
        while negative_cases.count(None):
            negative_cases.remove(None)
        while negative_cases.count(''):
            negative_cases.remove('')

        return (positive_cases, negative_cases)


class TestVaultRules(TestRulesBase):

    positive_cases = [
        'a',
        '0',
        '__vault_id____',
        '-_-_-_-_-_-_-_-',
        'snake_case_is_ok',
        'So-are-hyphonated-names',
        'a' * v.VAULT_ID_MAX_LEN
    ]

    negative_cases = [
        '',  # empty case should raise
        '.', '!', '@', '#', '$', '%',
        '^', '&', '*', '[', ']', '/',
        '@#$@#$@#^@%$@#@#@#$@!!!@$@$@',
        '\\', 'a' * (v.VAULT_ID_MAX_LEN + 1),
        None
    ]

    @validate(vault_id=v.VaultIdRule)
    def normal_vault_id(self, vault_id):
        return True

    @validate(vault_id=v.VaultIdRuleNoneOkay)
    def normal_vault_id_with_none(self, vault_id):
        return True

    def test_vault_id(self):

        for name in self.__class__.positive_cases:
            v.val_vault_id(name)

        for name in self.__class__.negative_cases:
            with self.assertRaises(v.ValidationFailed):
                v.val_vault_id()(name)

    def test_vault_rule(self):

        for p_case in self.__class__.positive_cases:
            self.assertTrue(self.normal_vault_id(p_case))

        for case in self.__class__.negative_cases:
            with self.assertRaises(errors.InvalidVault):
                self.normal_vault_id(case)

    def test_vault_with_none_rule(self):

        positive_cases, negative_cases = self.cases_with_none_okay()

        for p_case in positive_cases:
            self.assertTrue(self.normal_vault_id_with_none(p_case))

        for case in negative_cases:
            with self.assertRaises(errors.InvalidVault):
                self.normal_vault_id_with_none(case)


class TestBlockTypes(TestRulesBase):

    @validate(block=v.MetadataBlockType)
    def utilize_metadata_block(self, block):
        return True

    @validate(block=v.StorageBlockType)
    def utilize_storage_block(self, block):
        return True

    def setUp(self):

        self.project_id = create_project_name()
        self.vault_id = create_vault_name()

        block_id, block_data, block_size = create_block()
        self.metadata_block = api.Block(self.project_id,
                                        self.vault_id,
                                        block_id=block_id,
                                        data=block_data,
                                        block_type='metadata')
        storage_id = create_storage_block(block_id)
        self.storage_block = api.Block(self.project_id,
                                       self.vault_id,
                                       storage_id=storage_id,
                                       data=block_data,
                                       block_type='storage')

    def test_metadata_block_type(self):
        self.assertTrue(self.utilize_metadata_block(self.metadata_block))

        with self.assertRaises(errors.InvalidMetadataBlockType):
            self.utilize_metadata_block(self.storage_block)

    def test_storage_block_type(self):
        self.assertTrue(self.utilize_storage_block(self.storage_block))

        with self.assertRaises(errors.InvalidStorageBlockType):
            self.utilize_storage_block(self.metadata_block)


class TestMetadataBlockRules(TestRulesBase):

    positive_cases = [
        'da39a3ee5e6b4b0d3255bfef95601890afd80709',
        'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'ffffffffffffffffffffffffffffffffffffffff',
        'a' * 40,
    ]

    negative_cases = [
        '',
        '.',
        'a', '0', 'f', 'F', 'z', '#', '$', '?',
        'a39a3ee5e6b4b0d3255bfef95601890afd80709',  # one char short
        'da39a3ee5e6b4b0d3255bfef95601890afd80709a',  # one char long
        'DA39A3EE5E6B4B0D3255BFEF95601890AFD80709',
        'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF',
        'AaaAaaAaaaaAaAaaaAaaaaaaaAAAAaaaaAaaaaaa' * 2,
        'AaaAaaAaaaaAaAaaaAaaaaaaaAAAAaaaaAaaaaaa' * 3,
        'AaaAaaAaaaaAaAaaaAaaaaaaaAAAAaaaaAaaaaaa' * 4,
        None
    ]

    @validate(metadata_block_id=v.MetadataBlockIdRule)
    def normal_metadata_id(self, metadata_block_id):
        return True

    @validate(metadata_block_id=v.MetadataBlockIdRuleNoneOkay)
    def normal_metadata_id_with_none(self, metadata_block_id):
        return True

    @validate(metadata_block_ids=v.MetadataBlockIdIterableRule)
    def iterable_metadata_id(self, metadata_block_ids):
        return True

    @validate(metadata_block_ids=v.MetadataBlockIdIterableRuleNoneOkay)
    def iterable_metadata_id_with_none(self, metadata_block_ids):
        return True

    @validate(metadata_block_ids=v.MetadataBlockIdOffsetIterableRule)
    def iterable_metadata_id_with_offset(self, metadata_block_ids):
        return True

    @validate(metadata_block_ids=v.MetadataBlockIdOffsetIterableRuleNoneOkay)
    def iterable_metadata_id_with_offset_with_none(self, metadata_block_ids):
        return True

    def test_metadata_block_id(self):

        for blockid in self.__class__.positive_cases:
            v.val_metadata_block_id(blockid)

        for blockid in self.__class__.negative_cases:
            with self.assertRaises(v.ValidationFailed):
                v.val_metadata_block_id()(blockid)

    def test_metadata_iterable(self):

        v.val_metadata_block_id_iterable()(self.__class__.positive_cases)

        for blockid in self.__class__.negative_cases:
            with self.assertRaises(v.ValidationFailed):
                v.val_metadata_block_id_iterable()([blockid])

    def test_metadata_block_id_rule(self):

        for blockid in self.__class__.positive_cases:
            self.normal_metadata_id(blockid)

        for blockid in self.__class__.negative_cases:
            with self.assertRaises(errors.InvalidBlocks):
                self.normal_metadata_id(blockid)

    def test_metadata_block_id_with_none_rule(self):

        positive_cases, negative_cases = self.cases_with_none_okay()

        for blockid in positive_cases:
            self.normal_metadata_id_with_none(blockid)

        for blockid in negative_cases:
            with self.assertRaises(errors.InvalidBlocks):
                self.normal_metadata_id_with_none(blockid)

    def test_metadata_iterable_rule(self):

        positive_cases, negative_cases = self.iterable_cases()

        self.iterable_metadata_id(positive_cases)

        for blockid in negative_cases:
            with self.assertRaises(errors.InvalidBlocks):
                self.iterable_metadata_id([blockid])

        with self.assertRaises(errors.InvalidBlocks):
            self.iterable_metadata_id(None)

    def test_metadata_iterable_with_none_rule(self):

        positive_cases, negative_cases = self.iterable_cases()

        for blockid in positive_cases:
            self.iterable_metadata_id_with_none([blockid])

        self.iterable_metadata_id_with_none(None)

        for blockid in negative_cases:
            with self.assertRaises(errors.InvalidBlocks):
                self.iterable_metadata_id_with_none([blockid])
            with self.assertRaises(errors.InvalidBlocks):
                self.iterable_metadata_id_with_none([blockid])

    def test_metadata_offset_iterable_rule(self):

        for blockid in self.__class__.positive_cases:
            self.iterable_metadata_id_with_offset([(blockid, 0)])

        for blockid in self.__class__.negative_cases:
            with self.assertRaises(errors.IterableContentError):
                self.iterable_metadata_id_with_offset([(blockid, 0)])
            with self.assertRaises(errors.IterableContentError):
                self.iterable_metadata_id_with_offset([(0, blockid)])

    def test_metadata_offset_iterable_with_none_rule(self):

        positive_cases, negative_cases = self.iterable_cases()

        for blockid in positive_cases:
            self.iterable_metadata_id_with_offset_with_none([(blockid, 0)])

        self.iterable_metadata_id_with_offset_with_none(None)

        for blockid in negative_cases:
            with self.assertRaises(errors.IterableContentError):
                self.iterable_metadata_id_with_offset_with_none([(blockid, 0)])
            with self.assertRaises(errors.IterableContentError):
                self.iterable_metadata_id_with_offset_with_none([(0, blockid)])


class TestStorageBlockRules(TestRulesBase):

    positive_cases = [create_storage_block() for _ in range(0, 1000)]

    negative_cases = [
        '',
        'e7bf692b-ec7b-40ad-b0d1-45ce6798fb6z',  # note trailing z
        str(uuid.uuid4()).upper(),  # Force case sensitivity
        123456,
        None
    ]

    @validate(storage_block_id=v.StorageBlockIdRule)
    def normal_storage_id(self, storage_block_id):
        return True

    @validate(storage_block_id=v.StorageBlockIdRuleNoneOkay)
    def normal_storage_id_with_none(self, storage_block_id):
        return True

    @validate(storage_block_ids=v.StorageBlockIdIterableRule)
    def iterable_storage_id(self, storage_block_ids):
        return True

    @validate(storage_block_ids=v.StorageBlockIdIterableRuleNoneOkay)
    def iterable_storage_id_with_none(self, storage_block_ids):
        return True

    def test_storage_block_id(self):

        for storage_id in self.__class__.positive_cases:
            v.val_storage_block_id(storage_id)

        for storage_id in self.__class__.negative_cases:
            with self.assertRaises(v.ValidationFailed):
                v.val_storage_block_id()(storage_id)

    def test_storage_iterable(self):

        v.val_storage_block_id_iterable()(self.__class__.positive_cases)

        for blockid in self.__class__.negative_cases:
            with self.assertRaises(v.ValidationFailed):
                v.val_storage_block_id_iterable()([blockid])

    def test_storage_block_id_rule(self):

        for storage_id in self.__class__.positive_cases:
            self.normal_storage_id(storage_id)

        for storage_id in self.__class__.negative_cases:
            with self.assertRaises(errors.InvalidStorageBlocks):
                self.normal_storage_id(storage_id)

    def test_storage_block_id_with_none_rule(self):

        positive_cases, negative_cases = self.cases_with_none_okay()

        for storage_id in positive_cases:
            self.normal_storage_id_with_none(storage_id)

        for storage_id in negative_cases:
            with self.assertRaises(errors.InvalidStorageBlocks):
                self.normal_storage_id_with_none(storage_id)

    def test_storage_iterable_rule(self):

        positive_cases, negative_cases = self.iterable_cases()

        self.iterable_storage_id(positive_cases)

        for blockid in negative_cases:
            with self.assertRaises(errors.InvalidStorageBlocks):
                self.iterable_storage_id([blockid])

        with self.assertRaises(errors.InvalidStorageBlocks):
            self.iterable_storage_id(None)

    def test_storage_offset_iterable_with_none_rule(self):

        positive_cases, negative_cases = self.iterable_cases()

        for blockid in positive_cases:
            self.iterable_storage_id_with_none([blockid])

        self.iterable_storage_id_with_none(None)

        for blockid in negative_cases:
            with self.assertRaises(errors.InvalidStorageBlocks):
                self.iterable_storage_id_with_none([blockid])
            with self.assertRaises(errors.InvalidStorageBlocks):
                self.iterable_storage_id_with_none([blockid])


class TestFileRules(TestRulesBase):

    # Let's try try to append some UUIds and check for faileus
    positive_cases = [str(uuid.uuid4()) for _ in range(0, 1000)]

    negative_cases = [
        '',
        'e7bf692b-ec7b-40ad-b0d1-45ce6798fb6z',  # note trailing z
        str(uuid.uuid4()).upper(),  # Force case sensitivity
        None
    ]

    @validate(file_id=v.FileIdRule)
    def normal_file_id(self, file_id):
        return True

    @validate(file_id=v.FileIdRuleNoneOkay)
    def normal_file_id_with_none(self, file_id):
        return True

    def test_file_id(self):

        for fileid in self.__class__.positive_cases:
            v.val_file_id(fileid)

        for fileid in self.__class__.negative_cases:
            with self.assertRaises(v.ValidationFailed):
                v.val_file_id()(fileid)

    def test_file_id_rule(self):

        for file_id in self.__class__.positive_cases:
            self.normal_file_id(file_id)

        for file_id in self.__class__.negative_cases:
            with self.assertRaises(errors.InvalidFiles):
                self.normal_file_id(file_id)

    def test_get_file_id_none_okay(self):

        positive_cases, negative_cases = self.cases_with_none_okay()

        for file_id in positive_cases:
            self.normal_file_id_with_none(file_id)

        for file_id in negative_cases:
            with self.assertRaises(errors.InvalidFiles):
                self.normal_file_id_with_none(file_id)


class TestOffsetRules(TestRulesBase):

    positive_cases = [
        '0', '1', '2', '3', '55', '100',
        '101010', '99999999999999999999999999999'
    ]

    negative_cases = [
        '-1', '-23', 'O', 'zero', 'one', '-999', '1.0', '1.3',
        '0.0000000000001',
        None
    ]

    @validate(offset=v.OffsetRule)
    def normal_offset(self, offset):
        return True

    @validate(offset=v.OffsetRuleNoneOkay)
    def normal_offset_with_none(self, offset):
        return True

    def test_offset(self):

        for offset in self.__class__.positive_cases:
            v.val_offset()(offset)

        for offset in self.__class__.negative_cases:
            with self.assertRaises(v.ValidationFailed):
                v.val_offset()(offset)

    def test_offset_rule(self):

        for offset in self.__class__.positive_cases:
            self.assertTrue(self.normal_offset(offset))

        for offset in self.__class__.negative_cases:
            with self.assertRaises(errors.ParameterConstraintError):
                self.normal_offset(offset)

    def test_offset_with_none_rule(self):

        positive_cases, negative_cases = self.cases_with_none_okay()

        for offset in positive_cases:
            self.assertTrue(self.normal_offset_with_none(offset))

        for offset in negative_cases:
            with self.assertRaises(errors.ParameterConstraintError):
                self.normal_offset_with_none(offset, raiseme=True)


class TestOffsetNumericRules(TestRulesBase):

    positive_cases = [
        0, 1, 2, 3, 55, 100,
        101010, 99999999999999999999999999999
    ]

    negative_cases = [
        -1, -23, 'zero', 'one', -999, 1.0, 1.3,
        0.0000000000001,
        None
    ]

    @validate(offset=v.OffsetNumericRule)
    def normal_offset_numeric(self, offset):
        return True

    @validate(offset=v.OffsetNumericRuleNoneOkay)
    def normal_offset_numeric_with_none(self, offset):
        return True

    def test_offset(self):

        for offset in self.__class__.positive_cases:
            v.val_offset_numeric()(offset)

        for offset in self.__class__.negative_cases:
            with self.assertRaises(v.ValidationFailed):
                v.val_offset_numeric()(offset)

    def test_offset_rule(self):

        for offset in self.__class__.positive_cases:
            self.assertTrue(self.normal_offset_numeric(offset))

        for offset in self.__class__.negative_cases:
            with self.assertRaises(errors.ParameterConstraintError):
                self.normal_offset_numeric(offset)

    def test_offset_with_none_rule(self):

        positive_cases, negative_cases = self.cases_with_none_okay()

        for offset in positive_cases:
            self.assertTrue(self.normal_offset_numeric_with_none(offset))

        for offset in negative_cases:
            with self.assertRaises(errors.ParameterConstraintError):
                self.normal_offset_numeric_with_none(offset, raiseme=True)


class TestLimitRules(TestRulesBase):

    positive_cases = [
        0, 100, 100000000, 100
    ]

    negative_cases = [
        -1, 'blah', None
    ]

    @validate(limit=v.LimitRule)
    def normal_limit(self, limit):
        return True

    @validate(limit=v.LimitRuleNoneOkay)
    def normal_limit_with_none(self, limit):
        return True

    def test_limit(self):

        for limit in self.__class__.positive_cases:
            v.val_limit()(limit)

        for limit in self.__class__.negative_cases:
            with self.assertRaises(v.ValidationFailed):
                v.val_limit()(limit)

        v.val_limit(empty_ok=True)('')
        v.val_limit(none_ok=True)(None)

        with self.assertRaises(v.ValidationFailed):
            v.val_limit()('')

        with self.assertRaises(v.ValidationFailed):
            v.val_limit()(None)

    def test_limit_normal_rule(self):

        for limit in self.__class__.positive_cases:
            self.assertTrue(self.normal_limit(limit))

        for limit in self.__class__.negative_cases:
            with self.assertRaises(errors.ParameterConstraintError):
                self.normal_limit(limit)

    def test_limit_normal_with_none_rule(self):

        positive_cases, negative_cases = self.cases_with_none_okay()

        for limit in positive_cases:
            self.assertTrue(self.normal_limit_with_none(limit))

        for limit in negative_cases:
            with self.assertRaises(errors.ParameterConstraintError):
                self.normal_limit_with_none(limit)


class TestBoolRules(TestRulesBase):

    positive_cases = [
        True, False
    ]

    negative_cases = [
        0, 1, None, 'alibaba'
    ]

    @validate(b=v.BoolRule)
    def utilize_bool(self, b):
        return True

    def test_bool(self):
        for b in self.__class__.positive_cases:
            v.val_bool()(b)

        for b in self.__class__.negative_cases:
            with self.assertRaises(v.ValidationFailed):
                v.val_bool()(b)

    def test_bool_rule(self):
        for b in self.__class__.positive_cases:
            self.utilize_bool(b)

        for b in self.__class__.negative_cases:
            with self.assertRaises(errors.ParameterConstraintError):
                self.utilize_bool(b)


class TestIntRules(TestRulesBase):

    positive_cases = [
        -1, 0, 1, 1000, -1000
    ]

    negative_cases = [
        None, 'r', 'd', 'p'
    ]

    @validate(i=v.IntRule)
    def utilize_int(self, i):
        return True

    def test_int(self):
        for i in self.__class__.positive_cases:
            v.val_int()(i)

        for i in self.__class__.negative_cases:
            with self.assertRaises(v.ValidationFailed):
                v.val_int()(i)

    def test_int_rule(self):
        for i in self.__class__.positive_cases:
            self.utilize_int(i)

        for i in self.__class__.negative_cases:
            with self.assertRaises(errors.ParameterConstraintError):
                self.utilize_int(i)
