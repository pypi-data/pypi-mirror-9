"""
Deuce Client - Blocks API
"""
import json

from stoplight import validate

from deuceclient.api.block import Block
from deuceclient.common.validation import *


class Blocks(dict):
    """
    A collection of blocks
    """

    @validate(project_id=ProjectIdRule, vault_id=VaultIdRule)
    def __init__(self, project_id, vault_id):
        super(Blocks, self).__init__()
        self.__properties = {
            'marker': None,
            'project_id': project_id,
            'vault_id': vault_id
        }

    def serialize(self):
        return {
            'marker': self.marker,
            'project_id': self.project_id,
            'vault_id': self.vault_id,
            'blocks': {
                block_id: self[block_id].serialize()
                for block_id in self.keys()
            }
        }

    @staticmethod
    def deserialize(serialized_data):
        blocks = Blocks(serialized_data['project_id'],
                        serialized_data['vault_id'])
        blocks.marker = serialized_data['marker']
        blocks.update({
            k: Block.deserialize(v)
            for k, v in serialized_data['blocks'].items()
        })
        return blocks

    def to_json(self):
        return json.dumps(self.serialize())

    @staticmethod
    def from_json(serialized_data):
        json_data = json.loads(serialized_data)
        return Blocks.deserialize(json_data)

    @validate(key=MetadataBlockIdRule)
    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    @validate(key=MetadataBlockIdRule, val=MetadataBlockType)
    def __setitem__(self, key, val):
        if isinstance(val, Block):
            return dict.__setitem__(self, key, val)
        else:
            raise TypeError(
                '{0} can only contain Blocks'.format(self.__class__))

    @property
    def project_id(self):
        return self.__properties['project_id']

    @property
    def vault_id(self):
        return self.__properties['vault_id']

    @property
    def marker(self):
        return self.__properties['marker']

    @marker.setter
    @validate(value=MetadataBlockIdRuleNoneOkay)
    def marker(self, value):
        # Note: We could force that "marker" is in the dict;
        #   but then that would also unnecessarily force
        #   order-of-operations on how to use the object
        self.__properties['marker'] = value

    def __repr__(self):
        return '{0}: {1}'.format(type(self).__name__,
                                 dict.__repr__(self))

    def update(self, *args, **kwargs):
        # For use of Blocks.__setitem__ in order
        # to get validation of each entry in the incoming dictionary
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def add(self, block):
        if isinstance(block, Block):
            self[block.block_id] = block
        else:
            raise TypeError('block must be instance of deuceclient.api.Block')
