"""
Deuce Client - Utils - File Splitter - Uniform File Splitter
"""
import logging

from stoplight import validate

from deuceclient.api import Block, Blocks
from deuceclient.api.splitter import FileSplitterBase
from deuceclient.common.validation import *


class UniformSplitter(FileSplitterBase):
    """Splits the data into uniform chunks with exception of last chunk
    with whill be up to the specified size
    """

    def __init__(self, project_id, vault_id, input_io,
                 chunk_size=(1024 * 1024)):
        """
        :param input_io: file-like object providing read function
        :param chunk_size: uniform size in bytes to return at a time,
                           default 1KB
        """
        super(UniformSplitter, self).__init__(project_id, vault_id, input_io)
        self._chunk_size = chunk_size

    def configure(self, config):
        """
        Dict: config['UniformSplitter']['chunk_size']
              value: integer, uniform size in bytes to return at a time

        :failure: resets to previous value
        """
        old_value = self._chunk_size
        try:
            self._chunk_size = config['UniformSplitter']['chunk_size']
        except:
            # Roll-back
            self._chunk_size = old_value

    @property
    def chunk_size(self):
        return self._chunk_size

    def get_block(self):
        self._set_state('processing')
        data_offset = self.input_stream.tell()
        data = self.input_stream.read(self.chunk_size)

        # If len(data) is 0, then we've reached the end of the data source;
        # so don't create a block and return None instead.
        # Keeps from creating empty blocks.
        if len(data):
            return (data_offset, self._make_block(data))
        else:
            self._set_state(None)
            return (data_offset, None)
