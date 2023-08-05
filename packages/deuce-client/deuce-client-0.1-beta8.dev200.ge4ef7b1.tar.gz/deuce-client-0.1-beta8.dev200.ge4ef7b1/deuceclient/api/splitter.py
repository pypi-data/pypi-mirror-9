"""
Deuce Client - (File) Splitter API
"""
import abc

from stoplight import validate

from deuceclient.api.block import Block
from deuceclient.common import errors
from deuceclient.common.validation import *


class FileSplitterBase(object):
    """
    File Splitter Interface Class
    """
    __metaclass__ = abc.ABCMeta

    @validate(project_id=ProjectIdRule,
              vault_id=VaultIdRule,
              input_io=FileSplitterInputStreamRule)
    def __init__(self, project_id, vault_id, input_io):
        """
        :param input_io: file-like object providing a read and tell functions
        """
        self.__project_id = project_id
        self.__vault_id = vault_id
        self.__state = None
        self.__input_stream = input_io

    @property
    def state(self):
        return self.__state

    @validate(new_state=FileSplitterStateRule)
    def _set_state(self, new_state):
        self.__state = new_state

    @property
    def project_id(self):
        return self.__project_id

    @property
    def vault_id(self):
        return self.__vault_id

    @property
    def input_stream(self):
        return self.__input_stream

    @input_stream.setter
    @validate(input_io=FileSplitterInputStreamRule)
    def input_stream(self, input_io):
        if self.state is None:
            self.__input_stream = input_io
        else:
            raise RuntimeError('Invalid state to set new input_stream')

    @validate(count=IntRule)
    def get_blocks(self, count):
        """Get a series of blocks

        :returns: list of tuples containing the offset and block
        """
        blocks = []

        for block in [self.get_block() for _ in range(count)]:
            if block[1] is not None:
                blocks.append(block)

        return blocks

    def _make_block(self, data):
        block_id = Block.make_id(data)
        return Block(self.project_id, self.vault_id, block_id, data=data)

    @abc.abstractmethod
    def configure(self, config):
        """Configure the splitter

        :param config: dict - dictionary of the configuration values
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_block(self):
        """Get a block

        :returns: a tuple of (offset, api.Block) where the api.Block
                  contains the data the data, and offset is the offset
                  into the input_stream the block was read from
        """
        raise NotImplementedError()
