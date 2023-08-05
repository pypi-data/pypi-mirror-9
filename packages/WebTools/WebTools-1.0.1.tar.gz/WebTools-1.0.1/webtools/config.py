#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import importlib

#<----------------------------------------------------------------------------->

ENVIRONMENT_VARIABLE = 'WEBTOOLS_SETTINGS_MODULE'

#<----------------------------------------------------------------------------->

class LazySettings(object):
    """Lazily loads the settings module defined by the os environment variable.
    Based on the settings loader from Django.
    """

    def __init__(self):
        settings_module = os.environ.get(ENVIRONMENT_VARIABLE)
            
        if not settings_module:
            raise Exception('Environment variable {} is not defined.'\
                .format(ENVIRONMENT_VARIABLE))

        try:
            module = importlib.import_module(settings_module)
        except ImportError as e:
            raise ImportError('Unable to import {}: {}'.format(settings_module, e))

        for key in dir(module):
            if key.isupper() and not hasattr(self, key):
                setattr(self, key, getattr(module, key))

#<----------------------------------------------------------------------------->

settings = LazySettings()