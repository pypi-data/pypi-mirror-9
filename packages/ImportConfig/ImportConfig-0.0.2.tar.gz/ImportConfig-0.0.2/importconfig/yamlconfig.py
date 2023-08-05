"""YamlConfig - ``ImportConfig`` subclass for loading YAML files."""
from __future__ import print_function
from __future__ import unicode_literals


try:
    import yaml
except ImportError as exc_info:
    print('******************************************************')
    print('Ignore this message if you are installing ImportConfig')
    print('ImportError: {}'.format(exc_info))
    print('******************************************************')

from . import ImportConfig


class YamlConfig(ImportConfig):

    """YamlConfig will load a yaml file into a dict.

    Arguments:
        file_path (``str``): The path to the yaml file that will be loaded
        lazy (``bool``, optional): Do not load the yaml file immediately
            in the constructor. **default:** ``False``
    """

    def __init__(self, file_path, lazy=False):
        """YamlConfig constructor."""
        super(YamlConfig, self).__init__(yaml, file_path, lazy=lazy)
