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
