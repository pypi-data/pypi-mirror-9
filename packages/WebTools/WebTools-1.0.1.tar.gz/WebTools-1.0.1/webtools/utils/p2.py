#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Contains functions and classes compatible with Python 2
"""

import sys

#<----------------------------------------------------------------------------->

def raise_with_traceback(exp):
    tb = sys.exc_info()[2]
    raise exp, None, tb