#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Developer utility to generate and verify pathnames

GeneratePaths() takes a list of paths and returns a list of paths meeting
specified criteria (including access, filename extension, minimum size).

VerifyPaths() takes a list of paths and returns a boolean according to
whether the paths meet the specified criteria.
"""

__module__ = 'batchpath'
__version__ = '0.2'


# --- BEGIN CODE --- #

import os
from functools import partial


class GeneratePaths:
    """Process list of paths and return an iterable of verified paths."""
    def __init__(self):
        self.access = None
        self.extensions = None
        self.filetype = None
        self.minsize = None
        self.paths = None
        self.recursion = False

    def _generator_file(self):
        """Generator for `self.filetype` of 'file'"""
        for path in self.paths:
            if os.path.isfile(path):
                if isvalid(path, self.access, self.extensions,
                           minsize=self.minsize):
                    yield os.path.abspath(path)
            elif os.path.isdir(path):
                # pylint: disable=W0612
                for root, dnames, fnames in self._walker(path):
                    yield from self._generator_rebase(fnames, root)

    def _generator_other(self):
        """Generator for `self.filetype` other than file"""
        for path in self.paths:
            for root, dnames, fnames in self._walker(path):
                yield from self._generator_rebase(dnames, root)
                yield from self._generator_rebase(fnames, root)

    def _generator_rebase(self, names, root):
        """Component of _generator_other()"""
        return (_fixpath(root, base) for base in names if
                isvalid(_fixpath(root, base), self.access,
                        self.extensions, self.filetype, self.minsize))

    def _walker(self, path):
        """Walk a directory tree (optionally recursively)"""
        for root, dnames, fnames in _walk(self.recursion)(path):
            yield (root, dnames, fnames)

    def all(self, paths, access=None, recursion=False):
        """
        Iterates over `paths` (which may consist of files and/or directories).
        Removes duplicates and returns list of valid paths meeting access
        criteria.
        """
        self.__init__()
        self.access = access
        self.filetype = 'all'
        self.paths = paths
        self.recursion = recursion

        return _sorter(self._generator_other())

    def dirs(self, paths, access=None, recursion=False):
        """
        Iterates over `paths`. Removes duplicates and returns list of valid
        directories meeting access criteria.
        """
        self.__init__()
        self.access = access
        self.filetype = 'dir'
        self.paths = paths
        self.recursion = recursion

        return _sorter(self._generator_other())

    # pylint: disable=R0913
    def files(self, paths, access=None, extensions=None,
              minsize=None, recursion=False):
        """
        Iterates over `paths` (which may consist of files and/or directories).
        Removes duplicates and returns list of valid files meeting access,
        extension, and minimum size criteria.
        """
        self.__init__()
        self.access = access
        self.filetype = 'file'
        self.extensions = extensions
        self.minsize = minsize
        self.paths = paths
        self.recursion = recursion

        return _sorter(self._generator_file())


class VerifyPaths:
    """Verify list of paths"""
    def __init__(self):
        self.failures = []

    def all(self, paths, access=None):
        """Verify list of paths"""
        self.failures = [path for path in paths if not
                         isvalid(path, access, filetype='all')]

        return not self.failures

    def dirs(self, paths, access=None):
        """Verify list of directories"""
        self.failures = [path for path in paths if not
                         isvalid(path, access, filetype='dir')]

        return not self.failures

    def files(self, paths, access=None, extensions=None, minsize=None):
        """Verify list of files"""
        self.failures = [path for path in paths if not
                         isvalid(path, access, extensions, 'file', minsize)]

        return not self.failures


def _fixpath(root, base):
    """Return absolute, normalized, joined paths"""
    return os.path.abspath(os.path.normpath(os.path.join(root, base)))


def _sorter(generated):
    """Return a list of paths sorted by dirname & basename."""
    pairs = [(os.path.dirname(f), os.path.basename(f))
             for f in set(list(generated))]

    pairs.sort()

    return [os.path.join(pair[0], pair[1]) for pair in pairs]


def _walk(recursion):
    """Returns a recursive or non-recursive directory walker"""
    try:
        from scandir import walk as walk_function
    except ImportError:
        from os import walk as walk_function

    if recursion:
        walk = partial(walk_function)
    else:
        def walk(path):     # pylint: disable=C0111
            try:
                yield next(walk_function(path))
            except NameError:
                yield walk_function(path)
    return walk


def checkext(path, extensions):
    """Test whether file extension is contained in `extensions`."""
    return os.path.splitext(path)[1][1:] in extensions


def isvalid(path, access=None, extensions=None, filetype=None, minsize=None):
    """Check whether file meets access, extension, size, and type criteria."""
    return ((access is None or os.access(path, access)) and
            (extensions is None or checkext(path, extensions)) and
            (((filetype == 'all' and os.path.exists(path)) or
              (filetype == 'dir' and os.path.isdir(path)) or
              (filetype == 'file' and os.path.isfile(path))) or filetype is None)
            and (minsize is None or (not os.path.isfile(path) or
                                     os.path.getsize(path) > minsize)))
