#!/usr/bin/python3
"""
Deuce Client Command-line Interface
"""
from __future__ import print_function
import argparse
import json
import logging
import pprint
import sys

import deuceclient.api as api
import deuceclient.auth.nonauth as noauth
import deuceclient.auth.openstackauth as openstackauth
import deuceclient.auth.rackspaceauth as rackspaceauth
import deuceclient.client.deuce as client
import deuceclient.utils as utils


class ProgramArgumentError(ValueError):
    pass


def __api_operation_prep(log, arguments):
    """
    API Operation Common Functionality
    """
    # Parse the user data
    example_user_config_json = """
    {
        'user': <username>,
        'username': <username>,
        'user_name': <username>,
        'user_id': <userid>
        'tenant_name': <tenantname>,
        'tenant_id': <tenantid>,
        'apikey': <apikey>,
        'password': <password>,
        'token': <token>
    }

    Note: Only one of user, username, user_name, user_id, tenant_name,
          or tenant_id must be specified.

    Note: Only one of apikey, password, token must be specified.
        Token preferred over apikey or password.
        Apikey preferred over password.
    """
    auth_url = arguments.auth_service_url
    auth_provider = arguments.auth_service

    auth_data = {
        'user': {
            'value': None,
            'type': None
        },
        'credentials': {
            'value': None,
            'type': None
        }
    }

    def find_user(data):
        user_list = [
            ('user', 'user_name'),
            ('username', 'user_name'),
            ('user_name', 'user_name'),
            ('user_id', 'user_id'),
            ('tenant_name', 'tenant_name'),
            ('tenant_id', 'tenant_id'),
        ]

        for u in user_list:
            try:
                auth_data['user']['value'] = user_data[u[0]]
                auth_data['user']['type'] = u[1]
                return True
            except LookupError:
                pass

        return False

    def find_credentials(data):
        credential_list = ['token', 'password', 'apikey']
        for credential_type in credential_list:
            try:
                auth_data['credentials']['value'] = user_data[credential_type]
                auth_data['credentials']['type'] = credential_type
                return True
            except LookupError:
                pass

        return False

    user_data = json.load(arguments.user_config)
    if not find_user(user_data):
        sys.stderr.write('Unknown User Type.\n Example Config: {0:}'.format(
            example_user_config_json))
        sys.exit(-2)

    if not find_credentials(user_data):
        sys.stderr.write('Unknown Auth Type.\n Example Config: {0:}'.format(
            example_user_config_json))
        sys.exit(-3)

    # Setup the Authentication
    datacenter = arguments.datacenter

    asp = None
    if auth_provider == 'openstack':
        asp = openstackauth.OpenStackAuthentication

    elif auth_provider == 'rackspace':
        asp = rackspaceauth.RackspaceAuthentication

    elif auth_provider == 'none':
        asp = noauth.NonAuthAuthentication

    else:
        sys.stderr.write('Unknown Authentication Service Provider'
                         ': {0:}'.format(auth_provider))
        sys.exit(-4)

    auth_engine = asp(userid=auth_data['user']['value'],
                      usertype=auth_data['user']['type'],
                      credentials=auth_data['credentials']['value'],
                      auth_method=auth_data['credentials']['type'],
                      datacenter=datacenter,
                      auth_url=auth_url)

    # Deuce URL
    uri = arguments.url

    # Setup Agent Access
    deuce = client.DeuceClient(auth_engine, uri)

    return (auth_engine, deuce, uri)


def vault_list(log, arguments):
    """
    Create a vault with the given name
    """
    auth_engine, deuceclient, api_url = __api_operation_prep(log, arguments)

    # We need to authenticate to get the project id
    auth_engine.AuthToken

    try:
        project = api.Project(auth_engine.AuthTenantId)

        vault_marker = None
        while deuceclient.ListVaults(project, vault_marker):
            vault_marker = project.marker
            if vault_marker is None:
                break

        if len(project):
            print('Vaults:')
            for vault_id in project:
                print('\t{0:}'.format(vault_id))
            sys.exit(0)
        else:
            print('No Vaults available for the User')
            sys.exit(2)

    except Exception as ex:
        print('Error: {0:}'.format(ex))
        sys.exit(1)


def vault_create(log, arguments):
    """
    Create a vault with the given name
    """
    auth_engine, deuceclient, api_url = __api_operation_prep(log, arguments)

    try:
        deuceclient.CreateVault(arguments.vault_name)
        sys.exit(0)
    except Exception as ex:
        print('Error: {0:}'.format(ex))
        sys.exit(1)


def vault_exists(log, arguments):
    """
    Determine whether or not a vault of the given name exists
    """
    auth_engine, deuceclient, api_url = __api_operation_prep(log, arguments)

    try:
        if deuceclient.VaultExists(arguments.vault_name):
            print('Vault {0:} exists'.format(arguments.vault_name))
            sys.exit(0)
        else:
            print('Vault {0:} does NOT exist'.format(arguments.vault_name))
            sys.exit(1)
    except Exception as ex:
        print('Error determining if Vault {0:} exists: {1:}'
              .format(arguments.vault_name, ex))
        sys.exit(2)


def vault_stats(log, arguments):
    """
    Get the Stats for the vault with the given name
    """
    auth_engine, deuceclient, api_url = __api_operation_prep(log, arguments)

    try:
        vault = deuceclient.GetVault(arguments.vault_name)

        if deuceclient.GetVaultStatistics(vault):
            for k in vault.statistics.keys():
                print('{0:}:'.format(k), end='\t')
                pprint.pprint(vault.statistics[k])
        sys.exit(0)

    except Exception as ex:
        print('Error: {0:}'.format(ex))
        sys.exit(1)


def vault_delete(log, arguments):
    """
    Delete the vault with the given name
    """
    auth_engine, deuceclient, api_url = __api_operation_prep(log, arguments)

    try:
        vault = deuceclient.GetVault(arguments.vault_name)
        deuceclient.DeleteVault(vault)
        print('Deleted Vault {0}'.format(arguments.vault_name))
        sys.exit(0)

    except Exception as ex:
        print('Error: {0:}'.format(ex))
        sys.exit(1)


def block_list(log, arguments):
    """
    List the blocks in a vault
    """
    auth_engine, deuceclient, api_url = __api_operation_prep(log, arguments)

    try:
        vault = deuceclient.GetVault(arguments.vault_name)

        block_marker = arguments.marker
        while deuceclient.GetBlockList(vault,
                                       marker=block_marker,
                                       limit=arguments.limit):
            block_marker = vault.blocks.marker
            if block_marker is None:
                break

        if len(vault.blocks):
            print('Block List:')
            for key, block in vault.blocks.items():
                print('\t{0}'.format(block.block_id))
            sys.exit(0)

        else:
            print('No blocks in the Vault')
            sys.exit(2)

    except Exception as ex:
        print('Error: {0:}'.format(ex))
        sys.exit(1)


def block_upload(log, arguments):
    """
    Upload blocks to a vault
    """
    auth_engine, deuceclient, api_url = __api_operation_prep(log, arguments)

    try:
        vault = deuceclient.GetVault(arguments.vault_name)

        data = arguments.block_content.read()

        block_id = api.Block.make_id(data.encode())

        block = api.Block(project_id=auth_engine.AuthTenantId,
                          vault_id=arguments.vault_name,
                          block_id=block_id,
                          data=data)

        if deuceclient.UploadBlock(vault, block):
            print('Uploaded the block {0:} to deuce.'.format(block_id))
            sys.exit(0)

        else:
            sys.exit(1)

    except Exception as ex:
        print('Error: {0:}'.format(ex))
        sys.exit(1)


def block_delete(log, arguments):
    """
    Delete a block
    """
    auth_engine, deuceclient, api_url = __api_operation_prep(log, arguments)

    try:
        vault = deuceclient.GetVault(arguments.vault_name)

        block_id = arguments.block_id

        block = api.Block(project_id=auth_engine.AuthTenantId,
                          vault_id=arguments.vault_name,
                          block_id=block_id)

        if deuceclient.DeleteBlock(vault, block):
            print('Deleted the block {0:} from deuce.'.format(block_id))
            sys.exit(0)

        else:
            sys.exit(1)

    except Exception as ex:
        print('Error: {0:}'.format(ex))
        sys.exit(1)


def file_create(log, arguments):
    """
    Creates a file
    """
    auth_engine, deuceclient, api_url = __api_operation_prep(log, arguments)

    try:
        vault = deuceclient.GetVault(arguments.vault_name)

        file_id = deuceclient.CreateFile(vault)
        file_url = vault.files[file_id].url

        print('Created File')
        print('\tFile ID: {0}'.format(file_id))
        print('\tURL: {0}'.format(file_url))
        sys.exit(0)

    except Exception as ex:
        print('Error: {0:}'.format(ex))
        sys.exit(1)


def file_list(log, arguments):
    """
    List files in the vault
    """
    auth_engine, deuceclient, api_url = __api_operation_prep(log, arguments)

    try:
        vault = deuceclient.GetVault(arguments.vault_name)

        file_marker = None
        while deuceclient.ListFiles(vault,
                                    file_marker,
                                    limit=arguments.limit):
            file_marker = vault.files.marker
            if file_marker is None:
                break

        if len(vault.files):
            print('Files:')
            for file_id in vault.files:
                print('\t{0:}'.format(file_id))
            sys.exit(0)

        else:
            print('No files in the Vault')
            sys.exit(2)

    except Exception as ex:
        print('Error: {0:}'.format(ex))
        sys.exit(1)


def file_delete(log, arguments):
    """
    Delete a file
    """
    auth_engine, deuceclient, api_url = __api_operation_prep(log, arguments)

    try:
        vault = deuceclient.GetVault(arguments.vault_name)

        if deuceclient.DeleteFile(vault, arguments.file_id):
            print('Delete filed {0:} from Vault {1:}'
                  .format(arguments.file_id, arguments.vault_name))
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as ex:
        print('Error: {0:}'.format(ex))
        sys.exit(1)


def file_upload(log, arguments):
    """
    Upload a file
    """
    auth_engine, deuceclient, api_url = __api_operation_prep(log, arguments)

    try:
        vault = deuceclient.GetVault(arguments.vault_name)

        file_id = arguments.file_id
        if file_id is None:
            file_id = deuceclient.CreateFile(vault)
        else:
            vault.add_file(file_id)

        file_splitter = utils.UniformSplitter(vault.project_id,
                                              vault.vault_id,
                                              arguments.content)

        while True:

            block_list = vault.files[file_id].assign_from_data_source(
                file_splitter, append=True, count=10)

            if len(block_list):
                assignment_list = []

                for block, block_offset in block_list:
                    assignment_list.append((block.block_id, block_offset))

                blocks_to_upload = \
                    deuceclient.AssignBlocksToFile(vault,
                                                   file_id,
                                                   assignment_list)

                if len(blocks_to_upload):
                    for block, offset in block_list:
                        if block.block_id in blocks_to_upload:
                            vault.blocks[block.block_id] = block

                    deuceclient.UploadBlocks(vault, blocks_to_upload)

            else:
                break

        deuceclient.FinalizeFile(vault, file_id)

        file_url = vault.files[file_id].url

        print('Uploaded File')
        print('\tFile ID: {0}'.format(file_id))
        print('\tURL: {0}'.format(file_url))
        sys.exit(0)

    except Exception as ex:
        print('Error: {0:}'.format(ex))
        sys.exit(1)


def file_download(log, arguments):
    """
    Download a file
    """
    auth_engine, deuceclient, api_url = __api_operation_prep(log, arguments)

    try:
        vault = deuceclient.GetVault(arguments.vault_name)

        file_id = arguments.file_id
        filename = arguments.file_name

        deuceclient.DownloadFile(vault, file_id, filename)
        sys.exit(0)

    except Exception as ex:
        print('Error: {0:}'.format(ex))
        sys.exit(1)


def main():
    def parameter_add_vault_name(the_parser):
        the_parser.add_argument('--vault-name',
                                default=None,
                                required=True,
                                help="Vault Name")

    arg_parser = argparse.ArgumentParser(
        description="Cloud Backup Agent Status")
    arg_parser.add_argument('--user-config',
                            default=None,
                            type=argparse.FileType('r'),
                            required=True,
                            help='JSON file containing username and API Key')
    arg_parser.add_argument('--url',
                            default='127.0.0.1:8080',
                            type=str,
                            required=False,
                            help="Network Address for the Deuce Server."
                                 " Default: 127.0.0.1:8080")
    arg_parser.add_argument('-lg', '--log-config',
                            default=None,
                            type=str,
                            dest='logconfig',
                            help='log configuration file')
    arg_parser.add_argument('-dc', '--datacenter',
                            default='ord',
                            type=str,
                            dest='datacenter',
                            required=True,
                            help='Datacenter the system is in',
                            choices=['lon', 'syd', 'hkg', 'ord', 'iad', 'dfw'])
    arg_parser.add_argument('--auth-service',
                            default='rackspace',
                            type=str,
                            required=False,
                            help='Authentication Service Provider',
                            choices=['openstack', 'rackspace', 'none'])
    arg_parser.add_argument('--auth-service-url',
                            default=None,
                            type=str,
                            required=False,
                            help='Authentication Service Provider URL')
    sub_argument_parser = arg_parser.add_subparsers(title='subcommands')

    vault_parser = sub_argument_parser.add_parser('vault')
    vault_subparsers = vault_parser.add_subparsers(title='operations',
                                                   help='Vault Operations')

    vault_create_parser = vault_subparsers.add_parser('create')
    parameter_add_vault_name(vault_create_parser)
    vault_create_parser.set_defaults(func=vault_create)

    vault_exists_parser = vault_subparsers.add_parser('exists')
    parameter_add_vault_name(vault_exists_parser)
    vault_exists_parser.set_defaults(func=vault_exists)

    vault_stats_parser = vault_subparsers.add_parser('stats')
    parameter_add_vault_name(vault_stats_parser)
    vault_stats_parser.set_defaults(func=vault_stats)

    vault_delete_parser = vault_subparsers.add_parser('delete')
    parameter_add_vault_name(vault_delete_parser)
    vault_delete_parser.set_defaults(func=vault_delete)

    vault_list_parser = vault_subparsers.add_parser('list')
    vault_list_parser.set_defaults(func=vault_list)

    block_parser = sub_argument_parser.add_parser('blocks')
    parameter_add_vault_name(block_parser)
    block_subparsers = block_parser.add_subparsers(title='operations',
                                                   help='Block Operations')

    block_list_parser = block_subparsers.add_parser('list')
    block_list_parser.add_argument('--marker',
                                   default=None,
                                   required=False,
                                   type=str,
                                   help="Marker for retrieving partial "
                                        "contents. Unspecified means "
                                        "return everything.")
    block_list_parser.add_argument('--limit',
                                   default=None,
                                   required=False,
                                   type=int,
                                   help="Number of entries to return at most")
    block_list_parser.set_defaults(func=block_list)

    block_upload_parser = block_subparsers.add_parser('upload')
    block_upload_parser.add_argument('--block-content',
                                     default=None,
                                     required=True,
                                     type=argparse.FileType('r'),
                                     help="The block to be uploaded")
    block_upload_parser.set_defaults(func=block_upload)

    block_delete_parser = block_subparsers.add_parser('delete')
    block_delete_parser.add_argument('--block-id',
                                     default=None,
                                     required=True,
                                     type=str,
                                     help="Block ID of the block to be "
                                     "deleted")
    block_delete_parser.set_defaults(func=block_delete)

    file_parser = sub_argument_parser.add_parser('files')
    parameter_add_vault_name(file_parser)
    file_subparsers = file_parser.add_subparsers(title='operations',
                                                 help='File Operations')

    file_create_parser = file_subparsers.add_parser('create')
    file_create_parser.set_defaults(func=file_create)

    file_list_parser = file_subparsers.add_parser('list')
    file_list_parser.add_argument('--limit',
                                  default=None,
                                  required=False,
                                  type=int,
                                  help="Number of entries to return at most")
    file_list_parser.set_defaults(func=file_list)

    file_upload_parser = file_subparsers.add_parser('upload')
    file_upload_parser.add_argument('--file-id',
                                    default=None,
                                    required=False,
                                    type=str,
                                    help='File ID in the Vault for the new '
                                    'file. One will be created if not '
                                    'specified.')
    file_upload_parser.add_argument('--content',
                                    default=None,
                                    required=True,
                                    type=argparse.FileType('rb'),
                                    help='File to upload')
    file_upload_parser.set_defaults(func=file_upload)

    file_download_parser = file_subparsers.add_parser('download')
    file_download_parser.add_argument('--file-id',
                                      default=None,
                                      required=True,
                                      type=str,
                                      help='File ID in the Vault for the '
                                      'file.')
    file_download_parser.add_argument('--file-name',
                                      default=None,
                                      required=True,
                                      type=str,
                                      help='File name to store the file in')
    file_download_parser.set_defaults(func=file_download)

    file_delete_parser = file_subparsers.add_parser('delete')
    file_delete_parser.add_argument('--file-id',
                                    default=None,
                                    required=False,
                                    type=str,
                                    help='File ID in the Vault to be deleted')
    file_delete_parser.set_defaults(func=file_delete)

    arguments = arg_parser.parse_args()

    # If the caller provides a log configuration then use it
    # Otherwise we'll add our own little configuration as a default
    # That captures stdout and outputs to .deuce_client-py.log
    if arguments.logconfig is not None:
        logging.config.fileConfig(arguments.logconfig)
    else:
        lf = logging.FileHandler('.deuce_client-py.log')
        lf.setLevel(logging.DEBUG)

        log = logging.getLogger()
        log.addHandler(lf)
        log.setLevel(logging.DEBUG)

    # Build the logger
    log = logging.getLogger()

    arguments.func(log, arguments)


if __name__ == "__main__":
    sys.exit(main())
