"""
Deuce Client: Validation Functionality
"""
import re

from stoplight import Rule, ValidationFailed, validation_function

import deuceclient.common.errors as errors

PROJECT_ID_MAX_LEN = 128
VAULT_ID_MAX_LEN = 128
OPENSTRING_REGEX = re.compile('^[a-zA-Z0-9_\-]+$')
PROJECT_ID_REGEX = OPENSTRING_REGEX
VAULT_ID_REGEX = OPENSTRING_REGEX
METADATA_BLOCK_ID_REGEX = re.compile('\\b[0-9a-f]{40}\\b')
UUID_REGEX = re.compile(
    '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
FILE_ID_REGEX = UUID_REGEX
STORAGE_BLOCK_ID_REGEX = re.compile(
    METADATA_BLOCK_ID_REGEX.pattern[2:-2] + '_' + UUID_REGEX.pattern
)
OFFSET_REGEX = re.compile(
    '(?<![-.])\\b[0-9]+\\b(?!\\.[0-9])')
LIMIT_REGEX = re.compile(
    '(?<![-.])\\b[0-9]+\\b(?!\\.[0-9])')


@validation_function
def val_project_id(value):
    if not PROJECT_ID_REGEX.match(value):
        raise ValidationFailed('Invalid project id ({0})'.format(value))

    if len(value) > PROJECT_ID_MAX_LEN:
        raise ValidationFailed('Project ID exceeded max len ({0})'.format(
            VAULT_ID_MAX_LEN))


@validation_function
def val_vault_id(value):
    if not VAULT_ID_REGEX.match(value):
        raise ValidationFailed('Invalid vault id ({0})'.format(value))

    if len(value) > VAULT_ID_MAX_LEN:
        raise ValidationFailed('Vault ID exceeded max len ({0})'.format(
            VAULT_ID_MAX_LEN))


@validation_function
def val_file_id(value):
    if not FILE_ID_REGEX.match(value):
        raise ValidationFailed('Invalid File ID ({0})'.format(value))


@validation_function
def val_file_block_offset(value):
    if isinstance(value, int):
        if value < 0:
            raise ValidationFailed(
                'Invalid File Block Offset ({0})'.format(value))
    else:
        raise ValidationFailed('Invalid File Block Offset ({0})'.format(value))


@validation_function
def val_metadata_block_id(value):
    if not (isinstance(value, str) or isinstance(value, bytes)):
        raise ValidationFailed('Invalid Block ID ({0}) Type {1})'
                               .format(value, type(value)))
    if not METADATA_BLOCK_ID_REGEX.match(value):
        raise ValidationFailed('Invalid Block ID ({0})'.format(value))


@validation_function
def val_metadata_block_id_iterable(values):
    for value in values:
        val_metadata_block_id()(value)


@validation_function
def val_metadata_block_id_offset_iterable(values):
    for mbid, offset in values:
        val_metadata_block_id()(mbid)
        val_offset_numeric()(offset)


@validation_function
def val_storage_block_id(value):
    if not (isinstance(value, str) or isinstance(value, bytes)):
        raise ValidationFailed('Invalid Storage Block ID ({0}) Type {1})'
                               .format(value, type(value)))
    if not STORAGE_BLOCK_ID_REGEX.match(value):
        raise ValidationFailed('Invalid Storage Block ID ({0})'.format(value))


@validation_function
def val_storage_block_id_iterable(values):
    for value in values:
        val_storage_block_id()(value)


@validation_function
def val_offset(value):
    if not OFFSET_REGEX.match(value):
        raise ValidationFailed('Invalid offset ({0})'.format(value))


@validation_function
def val_offset_numeric(value):
    if isinstance(value, int):
        if value < 0:
            raise ValidationFailed('Invalid offset ({0})'.format(value))
    else:
        raise ValidationFailed('Invalid offset ({0})'.format(value))


@validation_function
def val_limit(value):
    if isinstance(value, int):
        if value < 0:
            raise ValidationFailed('Invalid Limit ({0}) - cannot be negative'
                .format(value))
    else:
        raise ValidationFailed('Invalid limit ({0}) - invalid type'
            .format(value))


@validation_function
def val_bool(value):
    if not isinstance(value, bool):
        raise ValidationFailed('Invalid type {0} instead of '
                               'Bool'.format(type(value)))


@validation_function
def val_int(value):
    if not isinstance(value, int):
        raise ValidationFailed('Invalid type {0} instead of int'
                               .format(type(value)))


@validation_function
def val_block_type_storage(value):
    try:
        if not value.block_type == 'storage':
            raise ValidationFailed('Invalid block type {0}'
                .format(value.block_type))
    except AttributeError:
        raise ValidationFailed('Invalid instance: {0}'.format(value))


@validation_function
def val_block_type_metadata(value):
    try:
        if not value.block_type == 'metadata':
            raise ValidationFailed('Invalid block type {0}'
                .format(value.block_type))
    except AttributeError:
        raise ValidationFailed('Invalid instance: {0}'.format(value))


@validation_function
def file_splitter_state_validation(value):
    if value not in (None, 'processing'):
        raise ValidationFailed('Invalid state {0}'.format(value))


@validation_function
def file_splitter_input_stream_validation(value):
    # if this is set up as an if-block then coverage fails
    # even though we go through all the use-cases. Leaving as-is
    # until we have a better solution and need it; the if-block
    # solution is really only to catch the issue should python
    # change and not raise an exception but instead do the better
    # thing of returning None...not likely going to happen
    try:
        getattr(value, 'read')
    except AttributeError:
        raise ValidationFailed('input stream must have read method')

    try:
        # tell is used to determine the starting offset into the
        # data stream that the block data was read from
        getattr(value, 'tell')
    except AttributeError:
        raise ValidationFailed('input stream must have tell method')


def _abort(error_code):
    abort_errors = {
        100: errors.InvalidProject,
        200: errors.InvalidVault,
        300: errors.InvalidFiles,
        400: errors.InvalidBlocks,
        403: errors.InvalidMetadataBlockType,
        500: errors.InvalidStorageBlocks,
        503: errors.InvalidStorageBlockType,
        600: errors.ParameterConstraintError,
        601: TypeError,  # Generic Type Error
        602: AttributeError,  # Generic Attribute Error
        700: errors.IterableContentError
    }
    raise abort_errors[error_code]


# Parameter Rules
BoolRule = Rule(val_bool(), lambda: _abort(600))
IntRule = Rule(val_int(), lambda: _abort(600))


ProjectIdRule = Rule(val_project_id(), lambda: _abort(100))

VaultIdRule = Rule(val_vault_id(), lambda: _abort(200))
VaultIdRuleNoneOkay = Rule(val_vault_id(none_ok=True), lambda: _abort(200))

MetadataBlockIdRule = Rule(val_metadata_block_id(), lambda: _abort(400))
MetadataBlockIdRuleNoneOkay = Rule(val_metadata_block_id(none_ok=True),
                                   lambda: _abort(400))
MetadataBlockIdIterableRule = Rule(val_metadata_block_id_iterable(),
                                   lambda: _abort(400))
MetadataBlockIdIterableRuleNoneOkay = Rule(val_metadata_block_id_iterable(
                                           none_ok=True),
                                           lambda: _abort(400))
MetadataBlockType = Rule(val_block_type_metadata(), lambda: _abort(403))
MetadataBlockIdOffsetIterableRule = \
    Rule(val_metadata_block_id_offset_iterable(),
         lambda: _abort(700))
MetadataBlockIdOffsetIterableRuleNoneOkay = \
    Rule(val_metadata_block_id_offset_iterable(none_ok=True),
         lambda: _abort(700))

StorageBlockIdRule = Rule(val_storage_block_id(), lambda: _abort(500))
StorageBlockIdRuleNoneOkay = Rule(val_storage_block_id(none_ok=True),
                                  lambda: _abort(500))
StorageBlockIdIterableRule = Rule(val_storage_block_id_iterable(),
                                  lambda: _abort(500))
StorageBlockIdIterableRuleNoneOkay = Rule(val_storage_block_id_iterable(
                                          none_ok=True),
                                          lambda: _abort(500))
StorageBlockType = Rule(val_block_type_storage(), lambda: _abort(503))

FileIdRule = Rule(val_file_id(), lambda: _abort(300))
FileIdRuleNoneOkay = Rule(val_file_id(none_ok=True),
                          lambda: _abort(300))

FileBlockOffsetRule = Rule(val_file_block_offset(), lambda: _abort(600))

FileSplitterStateRule = Rule(file_splitter_state_validation(none_ok=True),
                             lambda: _abort(600))
FileSplitterInputStreamRule = Rule(file_splitter_input_stream_validation(),
                                   lambda: _abort(602))

OffsetRule = Rule(val_offset(), lambda: _abort(600))
OffsetRuleNoneOkay = Rule(val_offset(none_ok=True), lambda: _abort(600))
OffsetNumericRule = Rule(val_offset_numeric(), lambda: _abort(600))
OffsetNumericRuleNoneOkay = Rule(val_offset_numeric(none_ok=True),
                                 lambda: _abort(600))

LimitRule = Rule(val_limit(), lambda: _abort(600))
LimitRuleNoneOkay = Rule(val_limit(none_ok=True), lambda: _abort(600))
