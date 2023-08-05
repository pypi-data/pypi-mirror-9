"""
Tests - Deuce Client - Client - Deuce - Storage Block
"""
import json
import urllib.parse

import httpretty

import deuceclient.client.deuce
import deuceclient.api as api
from deuceclient.tests import *


class ClientDeuceStorageBlockTests(ClientTestBase):

    def setUp(self):
        super(self.__class__, self).setUp()

        self.client = deuceclient.client.deuce.DeuceClient(self.authenticator,
                                                           self.apihost,
                                                           sslenabled=True)

    def tearDown(self):
        super(self.__class__, self).tearDown()

    @httpretty.activate
    def test_storage_block_download(self):
        storage_blockid = create_storage_block()
        blockid = hashlib.sha1(b'mock').hexdigest()

        check_data = {
            'ref-count': 2,
            'ref-modified': int(datetime.datetime.max.timestamp()),
        }

        httpretty.register_uri(httpretty.GET,
                               get_storage_block_url(self.apihost,
                                                     self.vault.vault_id,
                                                     storage_blockid),
                               content_type='application/octet-stream',
                               body="mock",
                               adding_headers={
                                   'x-block-reference-count':
                                   str(check_data['ref-count']),
                                   'x-ref-modified':
                                   str(check_data['ref-modified']),
                                   'x-storage-id': storage_blockid,
                                   'x-block-id': blockid,
                               },
                               status=200)
        block_before = api.Block(project_id=create_project_name(),
                                 vault_id=create_vault_name(),
                                 storage_id=storage_blockid,
                                 block_type='storage')
        block = self.client.DownloadBlockStorageData(self.vault,
                                                     block_before)
        self.assertEqual(block.data, b"mock")
        self.assertEqual(block.ref_count, check_data['ref-count'])
        self.assertEqual(block.ref_modified,
                         check_data['ref-modified'])
        self.assertEqual(block.storage_id, storage_blockid)
        self.assertEqual(block.block_id, blockid)

    @httpretty.activate
    def test_non_existent_storage_block_download(self):
        storage_blockid = create_storage_block()

        httpretty.register_uri(httpretty.GET,
                               get_storage_block_url(self.apihost,
                                                     self.vault.vault_id,
                                                     storage_blockid),
                               content_type='application/octet-stream',
                               body="mock",
                               status=404)
        block = api.Block(project_id=create_project_name(),
                          vault_id=create_vault_name(),
                          storage_id=storage_blockid,
                          block_type='storage')
        with self.assertRaises(RuntimeError) as deletion_error:
            self.client.DownloadBlockStorageData(self.vault, block)

    @httpretty.activate
    def test_storage_block_list(self):
        data = [create_storage_block() for _ in range(10)]
        expected_data = json.dumps(data)
        httpretty.register_uri(httpretty.GET,
                               get_storage_blocks_url(self.apihost,
                                                      self.vault.vault_id),
                               content_type='application/octet-stream',
                               body=expected_data,
                               status=200)
        blocks = self.client.GetBlockStorageList(self.vault)
        self.assertIsNone(self.vault.storageblocks.marker)
        self.assertEqual(blocks, data)

    @httpretty.activate
    def test_storage_block_list_with_next_batch(self):
        data = [create_storage_block() for _ in range(10)]
        expected_data = json.dumps(data)

        url = get_storage_blocks_url(self.apihost, self.vault.vault_id)
        url_params = urllib.parse.urlencode({'marker': data[0]})
        next_batch = '{0}?{1}'.format(url, url_params)
        httpretty.register_uri(httpretty.GET,
                               url,
                               content_type='application/octet-stream',
                               adding_headers={
                                   'x-next-batch': next_batch
                               },
                               body=expected_data,
                               status=200)
        blocks = self.client.GetBlockStorageList(self.vault)
        self.assertIsNotNone(self.vault.storageblocks.marker)
        self.assertEqual(self.vault.storageblocks.marker, data[0])
        self.assertEqual(blocks, data)

    @httpretty.activate
    def test_storage_block_list_error(self):
        httpretty.register_uri(httpretty.GET,
                               get_storage_blocks_url(self.apihost,
                                                      self.vault.vault_id),
                               status=500)

        with self.assertRaises(RuntimeError):
            self.client.GetBlockStorageList(self.vault)

    @httpretty.activate
    def test_storage_block_list_with_marker(self):
        block = create_block()
        data = sorted([create_storage_block(block[0])
                       for _ in range(3)])
        expected_data = json.dumps(data)
        httpretty.register_uri(httpretty.GET,
                               get_storage_blocks_url(self.apihost,
                                                      self.vault.vault_id),
                               content_type='application/octet-stream',
                               body=expected_data,
                               status=200)
        blocks = self.client.GetBlockStorageList(self.vault,
                                                 marker=data[0])
        self.assertIsNone(self.vault.storageblocks.marker)
        self.assertEqual(blocks, data)

    @httpretty.activate
    def test_storage_block_list_with_limit(self):
        block = create_block()
        data = sorted([create_storage_block(block[0])
                       for _ in range(5)])
        expected_data = json.dumps(data)
        httpretty.register_uri(httpretty.GET,
                               get_storage_blocks_url(self.apihost,
                                                      self.vault.vault_id),
                               content_type='application/octet-stream',
                               body=expected_data,
                               status=200)

        blocks = self.client.GetBlockStorageList(self.vault,
                                                 limit=5)
        self.assertIsNone(self.vault.storageblocks.marker)
        self.assertEqual(blocks, data)

    @httpretty.activate
    def test_storage_block_list_with_limit_and_marker(self):
        block = create_block()
        data = sorted([create_storage_block(block[0])
                       for _ in range(3)])
        expected_data = json.dumps(data)
        httpretty.register_uri(httpretty.GET,
                               get_storage_blocks_url(self.apihost,
                                                      self.vault.vault_id),
                               content_type='application/octet-stream',
                               body=expected_data,
                               status=200)

        blocks = self.client.GetBlockStorageList(self.vault,
                                                 limit=3,
                                                 marker=data[0])
        self.assertIsNone(self.vault.storageblocks.marker)
        self.assertEqual(blocks, data)

    @httpretty.activate
    def test_head_storage_block_non_existent(self):
        storage_blockid = create_storage_block()
        httpretty.register_uri(httpretty.HEAD,
                               get_storage_block_url(self.apihost,
                                                     self.vault.vault_id,
                                                     storage_blockid),
                               status=404)
        block = api.Block(project_id=create_project_name(),
                          vault_id=create_vault_name(),
                          storage_id=storage_blockid,
                          block_type='storage')
        with self.assertRaises(RuntimeError):
            self.client.HeadBlockStorage(self.vault, block)

    @httpretty.activate
    def test_head_storage_block(self):
        storage_blockid = create_storage_block()
        blockid = hashlib.sha1(b'mock').hexdigest()

        check_data = {
            'ref-count': 2,
            'ref-modified': int(datetime.datetime.max.timestamp()),
            'block-size': 200
        }

        httpretty.register_uri(httpretty.HEAD,
                               get_storage_block_url(self.apihost,
                                                     self.vault.vault_id,
                                                     storage_blockid),
                               adding_headers={
                                   'x-block-reference-count':
                                   check_data['ref-count'],
                                   'x-ref-modified':
                                   check_data['ref-modified'],
                                   'x-storage-id': storage_blockid,
                                   'x-block-id': blockid,
                                   'x-block-size':
                                   str(check_data['block-size']),
                                   'x-block-orphaned': True
                               },
                               status=204)
        block_before = api.Block(project_id=create_project_name(),
                                 vault_id=create_vault_name(),
                                 storage_id=storage_blockid,
                                 block_type='storage')
        block = self.client.HeadBlockStorage(self.vault, block_before)
        self.assertEqual(block.ref_count, check_data['ref-count'])
        self.assertEqual(block.ref_modified, check_data['ref-modified'])
        self.assertEqual(block.storage_id, storage_blockid)
        self.assertEqual(block.block_id, blockid)
        self.assertEqual(len(block), check_data['block-size'])
        self.assertTrue(block.block_orphaned)

    @httpretty.activate
    def test_delete_storage_block(self):
        storage_blockid = create_storage_block()
        httpretty.register_uri(httpretty.DELETE,
                               get_storage_block_url(self.apihost,
                                                     self.vault.vault_id,
                                                     storage_blockid),
                               status=204)
        block = api.Block(project_id=create_project_name(),
                          vault_id=create_vault_name(),
                          storage_id=storage_blockid,
                          block_type='storage')
        self.assertTrue(True,
                        self.client.DeleteBlockStorage(self.vault,
                                                       block))

    @httpretty.activate
    def test_delete_storage_block_non_existent(self):
        storage_blockid = create_storage_block()
        httpretty.register_uri(httpretty.DELETE,
                               get_storage_block_url(self.apihost,
                                                     self.vault.vault_id,
                                                     storage_blockid),
                               status=404)
        block = api.Block(project_id=create_project_name(),
                          vault_id=create_vault_name(),
                          storage_id=storage_blockid,
                          block_type='storage')
        with self.assertRaises(RuntimeError):
            self.client.DeleteBlockStorage(self.vault, block)
