#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Contains utility functions that are compatible with Python 3
"""

import sys

#<----------------------------------------------------------------------------->

def raise_with_traceback(exp):
    tb = sys.exc_info()[2]
    raise exp.with_traceback(tb)