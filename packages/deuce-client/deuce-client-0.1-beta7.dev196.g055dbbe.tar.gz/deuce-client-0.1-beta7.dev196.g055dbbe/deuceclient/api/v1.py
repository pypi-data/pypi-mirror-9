"""
Deuce Client - Deuce V1.0 Support
"""
from stoplight import validate

from deuceclient.common.validation import *


def get_base_path():
    return '/v1.0'


def get_vault_base_path():
    return '{0}/vaults'.format(get_base_path())


@validate(vault_id=VaultIdRule)
def get_vault_path(vault_id):
    return '{0}/{1}'.format(get_vault_base_path(),
                            vault_id)


@validate(vault_id=VaultIdRule)
def get_files_path(vault_id):
    return '{0}/files'.format(get_vault_path(vault_id))


@validate(vault_id=VaultIdRule, file_id=FileIdRule)
def get_file_path(vault_id, file_id):
    return '{0}/{1}'.format(get_files_path(vault_id), file_id)


@validate(vault_id=VaultIdRule, file_id=FileIdRule)
def get_fileblocks_path(vault_id, file_id):
    return '{0}/blocks'.format(get_file_path(vault_id, file_id))


@validate(vault_id=VaultIdRule)
def get_blocks_path(vault_id):
    return '{0}/blocks'.format(get_vault_path(vault_id))


@validate(vault_id=VaultIdRule, block_id=MetadataBlockIdRule)
def get_block_path(vault_id, block_id):
    return '{0}/{1}'.format(get_blocks_path(vault_id), block_id)


@validate(vault_id=VaultIdRule)
def get_storage_path(vault_id):
    return '{0}/storage'.format(get_vault_path(vault_id))


@validate(vault_id=VaultIdRule)
def get_storage_blocks_path(vault_id):
    return '{0}/blocks'.format(get_storage_path(vault_id))


@validate(vault_id=VaultIdRule, storage_block_id=StorageBlockIdRule)
def get_storage_block_path(vault_id, storage_block_id):
    return '{0}/{1}'.format(get_storage_blocks_path(vault_id),
                            storage_block_id)
