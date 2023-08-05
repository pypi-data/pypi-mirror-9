# -*- coding: utf-8 -*-
u"""JSON and YAML parsing with imports.

**Installation**::

    pip install importconfig

The special thing about ImportConfig is that it supports a notion
of "imports". You can import other json files in your json file
by specifying a "@file" value at any level in the config and it will
be expanded into that level.

A config file can be loaded lazily and the main config file will only be
loaded once it is called.

**Note:** keys/values defined in the top level document will take precedence
over those loaded in sub-documents.

**Example**::

    {
        "app_name": "foo",
        "logging": {
            "@file": "logging.json",
            "level": "debug"
        }
    }

**will translate into**::

    {
        "app_name": "foo",
        "logging": {
            "log_file": "/var/log/foo.log",
            "level": "debug"
        }
    }

**Contents of "logging.json"**::

    {
        "log_file": "/var/log/foo.log",
        "level": "info"
    }

.. todo::

    ✓ Support relative paths for ``@file's`` value
    ✓ Root document take precedence if the same key exists in the imported file
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from . import exceptions
from .importconfig import ImportConfig
from .jsonconfig import JsonConfig
from .jsonconfig import jsonconfig
from .yamlconfig import YamlConfig
from .yamlconfig import yamlconfig

__all__ = ('ImportConfig', 'JsonConfig', 'jsonconfig', 'YamlConfig',
           'yamlconfig', 'exceptions', )
__name__ = 'ImportConfig'
__url__ = 'https://github.com/Dinoshauer/ImportConfig'
__author__ = 'Kasper M. Jacobsen'
__email__ = 'k@mackwerk.dk'
__version__ = '0.0.4'
