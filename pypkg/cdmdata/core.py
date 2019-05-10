"""Common / Core functionality"""

# Copyright (c) 2019 Aubrey Barnard.
#
# This is free, open software licensed under the [MIT License](
# https://choosealicense.com/licenses/mit/).


import builtins
import io
import pathlib
import sys
import warnings


def open(file, mode='rt'):
    """
    Open and return the given file.

    Convenience function that takes anything that could be turned into a
    file-like object and returns a file-like object.

    file: str | pathlib.Path | io.TextIOBase | "-"
        Filename, path, stream, or '-', which indicates to use standard
        input.  Streams are passed through unmodified.
    mode: str
        Passed to `builtins.open`.
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


class PushbackIterator:
    """Iterator where you can push elements back into it"""

    def __init__(self, iterable):
        self._iter = iter(iterable)
        self._stack = []
        self._next = self._iter.__next__

    def __iter__(self):
        return self

    def __next__(self):
        return self._next()

    def push(self, item):
        self._stack.append(item)
        self._next = self.pop

    def pop(self):
        item = self._stack.pop()
        if len(self._stack) == 0:
            self._next = self._iter.__next__
        return item


def deprecated(message=None):
    """
    Return a decorator that wraps a function with the given warning
    message.
    """
    def mk_deprecated_wrapper(function):
        msg = (message
               if message is not None
               else f'`{function.__module__}.{function.__name__}` '
               'is deprecated')
        def wrap_deprecated(*args, **kwds):
            warnings.warn(DeprecationWarning(msg), stacklevel=2)
            return function(*args, **kwds)
        return wrap_deprecated
    return mk_deprecated_wrapper
