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
    """
    Open and return the given file.

    Convenience function that takes anything that could be turned into a
    file-like object and returns a file-like object.

    file:
        Filename, `pathlib.Path`, stream, or '-', which indicates to use
        standard input.  Streams are passed through unmodified.
    mode:
        As for `builtins.open`.
    """
    if file == '-':
        file = sys.stdin
    elif isinstance(file, str) or isinstance(file, pathlib.Path):
        file = builtins.open(file, mode)
    elif not isinstance(file, io.TextIOBase):
        raise ValueError('Not a file, stream, or filename: {!r}'
                         .format(file))
    return file


def lookup(name, namespaces=None, modules=None):
    """
    Look up the given name and return its binding.  Return `None` if not
    found.

    namespaces:
        Iterable of namespaces / dictionaries to search.
    modules:
        Iterable of modules / objects to search.
    """
    if namespaces is not None:
        for namespace in namespaces:
            if name in namespace:
                return namespace[name]
    if modules is not None:
        for module in modules:
            if hasattr(module, name):
                return getattr(module, name)
    return None
