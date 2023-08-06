#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

from webtools.wsgi import _local

#<----------------------------------------------------------------------------->

def main():
    unittest.main()

#<----------------------------------------------------------------------------->

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        """Set up the test framework."""
        pass
        
    def tearDown(self):
        # Clear thread-local variables.
        self.clear_globals()

    def clear_globals(self):
        _local.__release_local__()
