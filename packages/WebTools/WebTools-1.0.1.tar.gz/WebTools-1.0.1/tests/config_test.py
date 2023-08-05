#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

#<----------------------------------------------------------------------------->

ENVIRONMENT_VARIABLE = 'WEBTOOLS_SETTINGS_MODULE'

#<----------------------------------------------------------------------------->

class TestConfig(unittest.TestCase):

    def test_environment_variable(self):
        """Test if config can access the os environment"""

        with self.assertRaises(Exception):
            from webtools.config import settings

    def test_settings(self):
        """Test if config can access the settings module"""
        
        # test if config raises import error
        os.environ[ENVIRONMENT_VARIABLE] = "tests.resources.fake_settings"

        with self.assertRaises(ImportError):
            from webtools.config import settings

        # set the test settings module
        os.environ[ENVIRONMENT_VARIABLE] = "tests.resources.settings"

        from webtools.config import settings

        # test if attributes exist
        self.assertTrue(hasattr(settings, 'TEST_ATTRIBUTE'))
        self.assertEqual(settings.TEST_ATTRIBUTE, 'Hello World')