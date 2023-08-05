"""Base ``ImportConfig`` class.

ImportConfig can be subclassed for use with parsers that has a function called
``load`` to load file-like objects and parse them into python objects.
"""
from __future__ import print_function
from __future__ import unicode_literals

import collections
import os

from .exceptions import InvalidFilePathError


class ImportConfig(object):

    """Base class for YamlConfig and JsonConfig."""

    def __init__(self, loader, file_path, lazy=False):
        """ImportConfig constructor."""
        self.loader = loader
        self.file_path = file_path
        self.object = {}
        self.config = {}
        if not lazy:
            self.object = self._get_file_path(self.loader, self.file_path)
            self.config = self._expand(self.object)

    @staticmethod
    def _get_file_path(loader, file_path):
        """Check the file path and return the JSON loaded as a dict.

        Arguments:
            file_path (``str``): Path to the file to load

        Returns:
            ``dict``
        """
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file_obj:
                return loader.load(file_obj)
        raise InvalidFilePathError('{} is not a file!'.format(file_path))

    def _expand(self, input_dict):
        """Iterate on the config object and find @file keys.

        Returns:
            ``dict``
        """
        result = {}
        for key, value in input_dict.items():
            if key == '@file':
                result.update(self._get_file_path(self.loader, value))
            elif isinstance(value, collections.MutableMapping):
                result[key] = self._expand(value)
            else:
                result[key] = value
        res = {}
        for k, v in list(result.items()) + list(input_dict.items()):
            if k != '@file':
                res[k] = v
        return res

    def load(self):
        """Load up the expanded configuration.

        Returns:
            ``dict``
        """
        if not self.object:
            self.object = self._get_file_path(self.loader, self.file_path)
            self.config = self._expand(self.object)
            return self.config
        return self.config
