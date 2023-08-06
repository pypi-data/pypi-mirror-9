""" This module is adapted from: https://github.com/MongoEngine/mongoengine/blob/master/mongoengine/python_support.py
    This module original license: https://github.com/MongoEngine/mongoengine/blob/master/LICENSE """

import sys

PY3 = sys.version_info[0] == 3

if PY3:
    import codecs

    def b(s):
        """ :return: s converted to binary.  b('test') should be equivalent to b'test' """
        return codecs.latin_1_encode(s)[0]

    bin_type = bytes
    txt_type = str
else:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

    def b(s):
        """ identity function: conversion to binary is necessary only for Python 3 """
        return s

    bin_type = str
    txt_type = unicode

str_types = (bin_type, txt_type)
