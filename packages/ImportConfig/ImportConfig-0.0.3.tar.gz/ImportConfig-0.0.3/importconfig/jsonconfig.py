"""JsonConfig - ``ImportConfig`` subclass for loading JSON files."""
from __future__ import print_function
from __future__ import unicode_literals


try:
    import ujson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import json

from . import ImportConfig


class JsonConfig(ImportConfig):

    """JsonConfig will load a JSON file into a dict.

    It can be used with UltraJSON, simplejson or the built in json module.

    Arguments:
        file_path (``str``): The path to the JSON file that will be loaded
        lazy (``bool``, optional): Do not load the JSON file immediately
            in the constructor. **default:** ``False``
    """

    def __init__(self, file_path, lazy=False):
        """JsonConfig constructor."""
        super(JsonConfig, self).__init__(json, file_path, lazy=lazy)


def jsonconfig(file_path, lazy=False):
    """Will load a JSON file into a dict.

    Expanding any ``"@file"`` attributes that are found a long the way.
    It can be used with UltraJSON, simplejson or the built in json module.

    Note:
        Using this method is the same as calling
        ``JsonConfig(file_path, lazy=False).load()``

    Arguments:
        file_path (``str``): The path to the JSON file that will be loaded
        lazy (``bool``, optional): Do not load the JSON file immediately
            in the constructor. **default:** ``False``

    Returns:
        If ``lazy=True`` it will return an instance of ``JsonConfig``
        else a ``dict`` will be returned.
    """
    config = JsonConfig(file_path, lazy=lazy)
    if lazy:
        return config
    return config.load()
