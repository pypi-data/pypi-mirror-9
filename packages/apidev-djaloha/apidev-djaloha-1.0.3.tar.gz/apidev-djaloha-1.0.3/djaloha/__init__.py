# -*- coding: utf-8 -*-
"""djaloha is a tool for aloha-editor integration in a django app"""

VERSION = (1, 0, 3)


def get_version():
    """return version"""
    version = '%s.%s.%s' % (VERSION[0], VERSION[1], VERSION[2])
    return version

__version__ = get_version()
