#!/usr/bin/env python
# -*- coding: utf-8 -*-

VERSION = (0, 3, 1)

__author__ = 'Tzu-ping Chung'
__email__ = 'uranusjr@gmail.com'
__version__ = '.'.join(str(v) for v in VERSION)

# If we import directly, this may fail if six is not installed first.
# TODO: Find a better workaround for this problem.
try:
    from .plugin import SphinxDoctest   # noqa
except ImportError:
    pass
