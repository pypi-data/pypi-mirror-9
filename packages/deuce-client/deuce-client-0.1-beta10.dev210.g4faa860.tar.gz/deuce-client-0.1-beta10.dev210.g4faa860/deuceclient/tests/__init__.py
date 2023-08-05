"""
Tests - Deuce Client - Testing Support
"""
import datetime
import hashlib
import io
import os
import random
import time
import tempfile
from time import sleep as slowsleep
from unittest import TestCase
import uuid

import deuceclient
import deuceclient.auth.base
import deuceclient.api.project as api_project
import deuceclient.api.vault as api_vault


# NOTE(TheSriram): Let's monkey patch sleep to get tests
# to run faster
def fastsleep(seconds):
    speed_factor = 0.01
    slowsleep(seconds * speed_factor)


def create_vault_name():
    return 'vault_{0}'.format(str(uuid.uuid4()))


def create_project_name():
    return 'project_{0}'.format(str(uuid.uuid4()))


def get_base_path():
    return '/v1.0'


def get_vault_base_path():
    return '{0}/vaults'.format(get_base_path())


def get_vault_path(vault_name):
    return '{0}/{1}'.format(get_vault_base_path(), vault_name)


def get_blocks_path(vault_name):
    return '{0}/blocks'.format(get_vault_path(vault_name))


def get_block_path(vault_name, block_id):
    return '{0}/{1}'.format(get_blocks_path(vault_name), block_id)


def get_storage_path(vault_name):
    return '{0}/storage'.format(get_vault_path(vault_name))


def get_storage_blocks_path(vault_name):
    return '{0}/blocks'.format(get_storage_path(vault_name))


def get_storage_block_path(vault_name, block_id):
    return '{0}/{1}'.format(get_storage_blocks_path(vault_name), block_id)


def get_files_path(vault_name):
    return '{0}/files'.format(get_vault_path(vault_name))


def get_file_path(vault_name, file_id):
    return '{0}/{1}'.format(get_files_path(vault_name), file_id)


def get_fileblocks_path(vault_name, file_id):
    return '{0}/blocks'.format(get_file_path(vault_name, file_id))


def get_fileblock_path(vault_name, file_id, block_id):
    return '{0}/{1}'.format(get_fileblocks_path(vault_name, file_id), block_id)


def get_deuce_url(apihost):
    return 'https://{0}{1}'.format(apihost, get_base_path())


def get_vaults_url(apihost):
    return 'https://{0}{1}'.format(apihost, get_vault_base_path())


def get_vault_url(apihost, vault):
    return 'https://{0}{1}'.format(apihost, get_vault_path(vault))


def get_blocks_url(apihost, vault):
    return 'https://{0}{1}'.format(apihost, get_blocks_path(vault))


def get_storage_blocks_url(apihost, vault):
    return 'https://{0}{1}'.format(apihost, get_storage_blocks_path(vault))


def get_block_url(apihost, vault, block_id):
    return 'https://{0}{1}'.format(apihost, get_block_path(vault, block_id))


def get_storage_block_url(apihost, vault, storage_block_id):
    return 'https://{0}{1}'.format(apihost,
                                   get_storage_block_path(vault,
                                                          storage_block_id))


def get_files_url(apihost, vault):
    return 'https://{0}{1}'.format(apihost, get_files_path(vault))


def get_file_url(apihost, vault, file_id):
    return 'https://{0}{1}'.format(apihost, get_file_path(vault, file_id))


def get_file_blocks_url(apihost, vault, file_id):
    return 'https://{0}{1}'.format(apihost,
                                   get_fileblocks_path(vault, file_id))


def get_file_block_url(apihost, vault, file_id, block_id):
    return 'https://{0}{1}'.format(apihost,
                                   get_fileblock_path(vault,
                                                      file_id,
                                                      block_id))


def get_block_id(data):
    blockid_generator = hashlib.sha1()
    blockid_generator.update(data)
    return blockid_generator.hexdigest()


def create_block(block_size=100):
    block_data = os.urandom(block_size)
    block_id = get_block_id(block_data)
    return (block_id, block_data, block_size)


def create_blocks(block_count=1, block_size=100, uniform_sizes=False,
                  min_size=1, max_size=2000):
    block_sizes = []
    if uniform_sizes:
        block_sizes = [block_size for _ in range(block_count)]
    else:
        block_sizes = [random.randrange(min_size, max_size)
                       for block_size in range(block_count)]

    return [create_block(block_size) for block_size in block_sizes]


def create_file():
    return '{0}'.format(str(uuid.uuid4()))


def create_storage_block(block_id=None):
    if not block_id:
        block_id = hashlib.sha1(bytes(random.randrange(1000))).hexdigest()
    return '{0}_{1}'.format(block_id, str(uuid.uuid4()))


def make_reader(data_size, use_temp_file=False, null_data=False):
    """Make a reader that can be used for testing

    :param data_size: number of bytes to contain in the buffer
    :param use_temp_file: whether or not to use a temp file for the actual
                          data store as this exercises code differently
    :param null_data: bool - whether or not to use random data or data
                      initialized to all zeros (useful for dedup testing)
    :returns: File-like object that can be read using read(count)
    """
    # Create an byte-stream reader with a buffer of random bytes
    # of the requested size
    if null_data:
        data = bytes(bytes(data_size))
    else:
        data = bytes(os.urandom(data_size))

    if use_temp_file:
        tempf = tempfile.NamedTemporaryFile()
        tempf.write(data)
        tempf.seek(0)
        return tempf
    else:
        return io.BytesIO(data)


class FakeAuthenticator(deuceclient.auth.base.AuthenticationBase):

    def __init__(self, *args, **kwargs):
        super(FakeAuthenticator, self).__init__(*args, **kwargs)
        self.__tenantid = "tid_{0}".format(str(uuid.uuid4()))

        self.__token_data = {}
        self.__token_data['token'] = None
        self.__token_data['expires'] = datetime.datetime.utcnow()
        self.__token_data['lifetime_seconds'] = 3600  # 1 Hour

    @staticmethod
    def MakeToken(expires_in_seconds):
        expires_at = (datetime.datetime.utcnow() +
                      datetime.timedelta(seconds=expires_in_seconds))
        token = "token_{0}".format(str(uuid.uuid4()))
        return (expires_at, token)

    def GetToken(self, retry=5):
        expires, token = FakeAuthenticator.MakeToken(
            self.__token_data['lifetime_seconds'])
        if expires <= datetime.datetime.utcnow():
            if retry:
                return self.GetToken(retry - 1)
            else:
                return None
        else:
            self.__token_data['token'] = token
            self.__token_data['expires'] = expires
            return token

    def IsExpired(self, fuzz=0):
        test_time = (self.AuthExpirationTime() +
                    datetime.timedelta(seconds=fuzz))
        return (test_time >= datetime.datetime.utcnow())

    def AuthExpirationTime(self):
        return self.__token_data['expires']

    def _AuthToken(self):
        if self.IsExpired():
            return self.GetToken()

        elif self.IsExpired(fuzz=2):
            time.sleep(3)
            return self.GetToken()

        else:
            return self.__token_data['token']

    def _AuthTenantId(self):
        return self.__tenantid


class ClientTestBase(TestCase):

    def setUp(self):
        super(ClientTestBase, self).setUp()
        self.deuceclient_version = deuceclient.version()
        self.apihost = 'deuce-api-test'
        self.uripath = '/'
        self.expected_agent = 'Deuce-Client/{0:}'.format(
            self.deuceclient_version)
        self.expected_uri = "https://" + self.apihost + self.uripath
        self.authenticator = FakeAuthenticator(userid='cheshirecat',
                                               usertype='username',
                                               credentials='alice',
                                               auth_method='password',
                                               datacenter='wonderland',
                                               auth_url='down.the.rabbit.hole')

        self.project = api_project.Project(create_project_name())
        self.vault = api_vault.Vault(create_project_name(),
                                     create_vault_name())

    def tearDown(self):
        super(ClientTestBase, self).tearDown()

    @property
    def vault_name(self):
        return self.vault.vault_id


class VaultTestBase(ClientTestBase):

    def setUp(self):
        super(VaultTestBase, self).setUp()

        self.vault_id = create_vault_name()
        self.project_id = create_project_name()

    def tearDown(self):
        super(VaultTestBase, self).tearDown()

    def check_block_instance(self, a, b):
        self.assertEqual(a.project_id, b.project_id)
        self.assertEqual(a.vault_id, b.vault_id)
        if a.block_id is None:
            self.assertIsNone(b.block_id)
        else:
            self.assertEqual(a.block_id, b.block_id)
        if a.storage_id is None:
            self.assertIsNone(b.storage_id)
        else:
            self.assertEqual(a.storage_id, b.storage_id)
        self.assertEqual(a.ref_count, b.ref_count)
        self.assertEqual(a.ref_modified, b.ref_modified)
        self.assertEqual(len(a), len(b))
        self.assertEqual(a.block_orphaned, b.block_orphaned)
        self.assertEqual(a.block_type, b.block_type)

        # Note: Cannot check length as block data is not transferred
        #       and len(Block) requires the data be present

    def check_blocks(self, a, b):
        self.assertEqual(a.project_id, b.project_id)
        self.assertEqual(a.vault_id, b.vault_id)
        self.assertEqual(a.marker, b.marker)
        self.assertEqual(len(a), len(b))
        for k, v in a.items():
            self.assertIn(k, b)
            self.check_block_instance(v, b[k])
        for k, v in b.items():
            self.assertIn(k, a)
            self.check_block_instance(v, a[k])

    def check_file_instance(self, a, b):
        self.assertEqual(a.project_id, b.project_id)
        self.assertEqual(a.vault_id, b.vault_id)
        self.assertEqual(a.file_id, b.file_id)
        self.assertEqual(a.url, b.url)
        self.assertEqual(a._File__properties['maximum_offset'],
                         b._File__properties['maximum_offset'])
        self.check_blocks(a.blocks, b.blocks)
        self.assertEqual(len(a), len(b))
        for k, v in a.offsets.items():
            self.assertIn(k, b.offsets)
            self.assertEqual(v, b[k])

        for k, v in b.offsets.items():
            self.assertIn(k, a.offsets)
            self.assertEqual(v, a[k])

    def check_files(self, a, b):
        self.assertEqual(a.project_id, b.project_id)
        self.assertEqual(a.vault_id, b.vault_id)
        self.assertEqual(a.marker, b.marker)
        self.assertEqual(len(a), len(b))

        # Ensure everything in 'a' is in 'b'
        for k, v in a.items():
            self.assertIn(k, b)
            self.check_file_instance(v, b[k])
        # Ensure the reverse as well just in case
        for k, v in b.items():
            self.assertIn(k, a)
            self.check_file_instance(v, a[k])

    def check_vault(self, a, b):
        self.assertEqual(a.project_id, b.project_id)
        self.assertEqual(a.vault_id, b.vault_id)
        self.check_blocks(a.blocks, b.blocks)
        self.check_blocks(a.storageblocks, b.storageblocks)
        self.check_files(a.files, b.files)
