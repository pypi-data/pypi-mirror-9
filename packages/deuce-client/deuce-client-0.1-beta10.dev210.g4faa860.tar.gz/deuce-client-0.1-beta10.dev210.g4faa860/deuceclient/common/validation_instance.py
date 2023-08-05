"""
Deuce Client: Instance Validation Functionality
"""
from stoplight import Rule, ValidationFailed, validation_function

import deuceclient.api.project as api_project
import deuceclient.api.vault as api_vault
import deuceclient.api.block as api_block
import deuceclient.api.splitter as api_splitter
import deuceclient.common.errors as errors


@validation_function
def val_project_instance(value):
    if not isinstance(value, api_project.Project):
        raise ValidationFailed('project must be deuceclient.api.Project')


@validation_function
def val_vault_instance(value):
    if not isinstance(value, api_vault.Vault):
        raise ValidationFailed('vault must be deuceclient.api.Vault')


@validation_function
def val_block_instance(value):
    if not isinstance(value, api_block.Block):
        raise ValidationFailed('block must be deuceclient.api.Block')


@validation_function
def val_file_splitter_instance(value):
    if not isinstance(value, api_splitter.FileSplitterBase):
        raise ValidationFailed('splitter must be '
                               'deuceclient.api.splitter.FileSplitterBase')


def _abort_instance(error_code):
    abort_errors = {
        101: errors.InvalidProjectInstance,
        201: errors.InvalidVaultInstance,
        # 301: errors.InvalidFiles,
        # 401: errors.InvalidBlocks,
        402: errors.InvalidBlockInstance,
        # 501: errors.InvalidStorageBlocks,
        601: errors.InvalidFileSplitterType
    }
    raise abort_errors[error_code]

ProjectInstanceRule = Rule(val_project_instance(),
                           lambda: _abort_instance(101))
VaultInstanceRule = Rule(val_vault_instance(), lambda: _abort_instance(201))
BlockInstanceRule = Rule(val_block_instance(), lambda: _abort_instance(402))
FileSplitterInstanceRule = Rule(val_file_splitter_instance(),
                                lambda: _abort_instance(601))
