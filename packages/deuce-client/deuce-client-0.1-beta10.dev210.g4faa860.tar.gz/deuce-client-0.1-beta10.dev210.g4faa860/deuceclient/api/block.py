"""
Deuce Client - Block API
"""
import hashlib
import json

from stoplight import validate

from deuceclient.common.validation import *


class Block(object):

    @staticmethod
    def make_id(data):
        sha1 = hashlib.sha1()
        sha1.update(data)
        return sha1.hexdigest().lower()

    # TODO: Add a validator for data, ref_count, ref_modified
    @validate(project_id=ProjectIdRule,
              vault_id=VaultIdRule,
              block_id=MetadataBlockIdRuleNoneOkay,
              storage_id=StorageBlockIdRuleNoneOkay)
    def __init__(self, project_id, vault_id, block_id=None,
                 storage_id=None, data=None,
                 ref_count=None, ref_modified=None, block_size=None,
                 block_orphaned='indeterminate', block_type='metadata'):

        # NOTE(TheSriram): By default, the block_type is set to be metadata
        # but this can be overridden when instantiating to either be metadata
        # or storage

        if block_id is None and storage_id is None:
            raise ValueError("Both storage_id and block_id cannot be None")

        elif block_type not in ('metadata', 'storage'):
            raise ValueError(
                'Invalid block_type Status Value: {0} '
                'Accepted values are metadata '
                'and storage'.format(block_type))
        elif block_type == 'metadata' and block_id is None:
            raise ValueError(
                'block_id cannot be None, if block_type is set to metadata'
            )
        elif block_type == 'storage' and storage_id is None:
            raise ValueError(
                'storage_id cannot be None, if block_type is set to storage'
            )
        else:
            self.__properties = {
                'project_id': project_id,
                'vault_id': vault_id,
                'block_id': block_id,
                'storage_id': storage_id,
                'data': data,
                'references': {
                    'count': ref_count,
                    'modified': ref_modified,
                },
                'block_size': block_size,
                'block_orphaned': block_orphaned,
                'block_type': block_type
            }

    def serialize(self):
        return {
            'project_id': self.project_id,
            'vault_id': self.vault_id,
            'block_id': self.block_id,
            'storage_id': self.storage_id,
            'references': {
                'count': self.ref_count,
                'modified': self.ref_modified
            },
            'block_size': self.__properties['block_size'],
            'block_orphaned': self.block_orphaned,
            'block_type': self.block_type
        }

    @staticmethod
    def deserialize(serialized_data):
        return Block(serialized_data['project_id'],
                     serialized_data['vault_id'],
                     block_id=serialized_data['block_id'],
                     storage_id=serialized_data['storage_id'],
                     ref_count=serialized_data['references']['count'],
                     ref_modified=serialized_data['references']['modified'],
                     block_size=serialized_data['block_size'],
                     block_orphaned=serialized_data['block_orphaned'],
                     block_type=serialized_data['block_type'])

    def to_json(self):
        return json.dumps(self.serialize())

    @staticmethod
    def from_json(serialized_data):
        json_data = json.loads(serialized_data)
        return Block.deserialize(json_data)

    @property
    def project_id(self):
        return self.__properties['project_id']

    @property
    def vault_id(self):
        return self.__properties['vault_id']

    @property
    def block_id(self):
        return self.__properties['block_id']

    @property
    def block_type(self):
        return self.__properties['block_type']

    @block_id.setter
    @validate(value=MetadataBlockIdRuleNoneOkay)
    def block_id(self, value):
        if self.__properties['block_type'] == 'metadata':
            raise ValueError('Cannot update block_id '
                             'for metadata blocks')
        else:
            self.__properties['block_id'] = value

    @property
    def storage_id(self):
        return self.__properties['storage_id']

    @storage_id.setter
    @validate(value=StorageBlockIdRule)
    def storage_id(self, value):
        if self.__properties['block_type'] == 'storage':
            raise ValueError('Cannot update storage_id '
                             'for storage blocks')
        else:
            self.__properties['storage_id'] = value

    @property
    def data(self):
        return self.__properties['data']

    # TODO: Add a validator
    @data.setter
    def data(self, value):
        self.__properties['data'] = value

    def __len__(self):
        if self.data is None:
            if self.__properties['block_size'] is None:
                return 0
            else:
                return self.__properties['block_size']
        else:
            return len(self.data)

    def set_block_size(self, value):
        self.__properties['block_size'] = value

    @property
    def block_orphaned(self):
        return self.__properties['block_orphaned']

    @block_orphaned.setter
    @validate(value=BoolRule)
    def block_orphaned(self, value):
        self.__properties['block_orphaned'] = value

    @property
    def ref_count(self):
        return self.__properties['references']['count']

    # TODO: Add a validator
    @ref_count.setter
    def ref_count(self, value):
        self.__properties['references']['count'] = value

    @property
    def ref_modified(self):
        return self.__properties['references']['modified']

    # TODO: Add a validator
    @ref_modified.setter
    def ref_modified(self, value):
        self.__properties['references']['modified'] = value
