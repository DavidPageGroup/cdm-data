"""Common / Core functionality"""

# Copyright (c) 2019 Aubrey Barnard.
#
# This is free, open software licensed under the [MIT License](
# https://choosealicense.com/licenses/mit/).


import builtins
import io
import pathlib
import sys


def open(file, mode='rt'):
    if file == '-':
        file = sys.stdin
    elif isinstance(file, str) or isinstance(file, pathlib.Path):
        file = builtins.open(file, mode)
    elif not isinstance(file, io.TextIOBase):
        raise ValueError('Not a file, stream, or filename: {!r}'
                         .format(file))
    return file


def lookup(name, namespaces=None, modules=None):
    if namespaces is not None:
        for namespace in namespaces:
            if name in namespace:
                return namespace[name]
    if modules is not None:
        for module in modules:
            if hasattr(module, name):
                return getattr(module, name)
    return None
