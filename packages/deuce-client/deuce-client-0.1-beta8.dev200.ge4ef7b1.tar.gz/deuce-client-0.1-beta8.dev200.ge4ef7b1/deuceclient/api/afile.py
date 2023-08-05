"""
Deuce Client - File API
"""
import json

from stoplight import validate

from deuceclient.api.blocks import Blocks
from deuceclient.api.splitter import FileSplitterBase
from deuceclient.common.validation import *


class File(object):

    @validate(project_id=ProjectIdRule,
              vault_id=VaultIdRule,
              file_id=FileIdRuleNoneOkay)
    def __init__(self, project_id, vault_id, file_id=None, url=None):
        self.__properties = {
            'project_id': project_id,
            'vault_id': vault_id,
            'file_id': file_id,
            'blocks': Blocks(project_id=project_id,
                             vault_id=vault_id),
            'offsets': {},
            'maximum_offset': 0,
            'url': url
        }

    def serialize(self):
        return {
            'project_id': self.project_id,
            'vault_id': self.vault_id,
            'file_id': self.file_id,
            'maximum_offset': self.__properties['maximum_offset'],
            'url': self.url,
            'offsets': self.offsets,
            'blocks': self.blocks.serialize()
        }

    @staticmethod
    def deserialize(serialized_data):
        new_file = File(serialized_data['project_id'],
                        serialized_data['vault_id'],
                        file_id=serialized_data['file_id'],
                        url=serialized_data['url'])
        new_file.__properties['maximum_offset'] =\
            serialized_data['maximum_offset']
        new_file.__properties['offsets'] = serialized_data['offsets']
        new_file.__properties['blocks'] = Blocks.deserialize(
            serialized_data['blocks'])
        return new_file

    def to_json(self):
        return json.dumps(self.serialize())

    @staticmethod
    def from_json(serialized_data):
        json_data = json.loads(serialized_data)
        return File.deserialize(json_data)

    @validate(offset=OffsetNumericRule)
    def _update_maximum_offset(self, offset):
        self.__properties['maximum_offset'] = max(
            self.__properties['maximum_offset'],
            offset)

    def __len__(self):
        returnValue = 0
        if len(self.offsets):
            returnValue = self.__properties['maximum_offset']
            try:
                block_at_offset = self.get_block_for_offset(returnValue)
                the_block = self.blocks[block_at_offset]
                returnValue = returnValue + len(the_block)
            except KeyError:
                pass

        return returnValue

    @property
    def project_id(self):
        return self.__properties['project_id']

    @property
    def vault_id(self):
        return self.__properties['vault_id']

    @property
    def file_id(self):
        return self.__properties['file_id']

    @property
    def url(self):
        return self.__properties['url']

    @file_id.setter
    @validate(value=FileIdRule)
    def file_id(self, value):
        self.__properties['file_id'] = value

    @property
    def blocks(self):
        return self.__properties['blocks']

    @property
    def offsets(self):
        return self.__properties['offsets']

    @validate(block=MetadataBlockType)
    def add_block(self, block):
        if block.block_id not in self.blocks:
            self.blocks[block.block_id] = block

    @validate(block_id=MetadataBlockIdRule, offset=FileBlockOffsetRule)
    def assign_block(self, block_id, offset):
        self.offsets[str(offset)] = block_id
        self._update_maximum_offset(offset)

    @validate(offset=FileBlockOffsetRule)
    def get_block_for_offset(self, offset):
        return self.__properties['offsets'][str(offset)]

    @validate(block_id=MetadataBlockIdRule)
    def get_offsets_for_block(self, block_id):
        offsets = []
        for offset, block in self.offsets.items():
            if block == block_id:
                offsets.append(int(offset))
        return offsets

    @validate(append=BoolRule,
              count=IntRule)
    def assign_from_data_source(self, splitter, append=False, count=1):
        if not isinstance(splitter, FileSplitterBase):
            raise errors.InvalidFileSplitterType(
                'splitter must be deuceclient.api.splitter.FileSplitterBase')

        base_offset = 0

        if not append:
            if len(self.blocks):
                raise errors.InvalidContentError('File has data already')

        added_blocks = []
        for block_offset, block in splitter.get_blocks(count):

            self.add_block(block)

            if append:
                actual_offset = len(self)
            else:
                actual_offset = block_offset

            self.assign_block(block.block_id, actual_offset)
            added_blocks.append((block, actual_offset))
        return added_blocks
