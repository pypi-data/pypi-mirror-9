# -*- coding: utf-8 -*-
'''
Make file system paths object oriented...
'''

import glob
import fnmatch
import os
import posixpath
import time


class alias(object):
    '''Alias descriptor, wraps a function.'''

    def __init__(self, fn, returns_typ=False):
        self.fn = fn
        self.returns_typ = returns_typ

    def __get__(self, obj, typ=None):
        val = self.fn(obj)
        if self.returns_typ:
            return typ(val)
        return val


class FilePath(str):
    '''Object Oriented FilePaths'''

    default_time_format = '%d %b %Y %H:%M:%S'

    def __repr__(self):
        return "FilePath('{0}')".format(self)

    def __eq__(self, other):
        if isinstance(other, FilePath):
            return self.normpath == other.normpath
        return super(FilePath, self).__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        '''Returns a :class:`FilePath`'''

        return FilePath(super(FilePath, self).__add__(other))

    def __iadd__(self, other):
        '''Uses :func:`os.path.join` in place replacing the current
        :class:`FilePath` with the result.'''

        self = self + other
        return self

    exists = alias(os.path.exists)
    isfile = alias(os.path.isfile)
    isdir = alias(os.path.isdir)
    islink = alias(os.path.islink)
    listdir = alias(os.listdir)
    basename = alias(os.path.basename, returns_typ=True)
    dirname = alias(os.path.dirname, returns_typ=True)
    abspath = alias(os.path.abspath, returns_typ=True)
    normpath = alias(os.path.normpath, returns_typ=True)
    realpath = alias(os.path.realpath, returns_typ=True)
    expanduser = alias(os.path.expanduser, returns_typ=True)
    expandvars = alias(os.path.expandvars, returns_typ=True)

    def glob(self, pattern):
        '''Glob relative to :class:`FilePath`'''

        return glob.glob(self.join(pattern))

    def join(self, *args):
        '''wraps :func:`os.path.join`'''

        return FilePath(os.path.join(self, *args))

    def walk_up(self, steps=20):
        '''Walk up a directory tree. Similar to os.walk but excludes stepping
        into subdirs.

        :param steps: Maximum steps taken up a tree
        :returns: root as :class:`FilePath`, [subdirs...], [files...]
        '''

        root = self

        for i in xrange(steps):
            files = set(root.listdir)
            dirs = set([f for f in files if root.join(f).isdir])
            files -= dirs
            yield root, sorted(list(dirs)), sorted(list(files))

            root = root.dirname

    def walk(self):
        '''Walk down a directory tree.

        :returns: root as :class:`FilePath`, [subdirs...], [files...]

        usage::
            top = FilePath('.')
            for root, subdirs, files in top.walk():
                for f in files:
                    print root.join(f)
        '''

        for root, subdirs, files in os.walk(self):
            yield FilePath(root), subdirs, files

    @property
    def split(self):
        '''wraps :func:`os.path.split`'''

        head, tail = os.path.split(self)

        return FilePath(head), tail

    @property
    def splitext(self):
        name, ext = os.path.splitext(self)

        return FilePath(name), ext

    # Stat properties and methods
    @property
    def stat(self):
        '''Returns stat or lstat of path'''

        if self.islink:
            return os.lstat(self)
        return os.stat(self)

    @property
    def modified(self):
        return self.stat.st_mtime

    def format_modified(self, formatter=default_time_format):
        '''Returns modified time formatted

        :param formatter: :func:`time.strftime` format string
            defaults to "%d %b %Y %H:%M:%S"
        '''

        local = time.localtime(self.modified)
        return time.strftime(formatter, local)

    @property
    def accessed(self):
        return self.stat.st_atime

    def format_accessed(self, formatter=default_time_format):
        '''Returns last access time formatted

        :param formatter: :func:`time.strftime` format string
            defaults to "%d %b %Y %H:%M:%S"
        '''

        local = time.localtime(self.accessed)
        return time.strftime(formatter, local)

    @property
    def created(self):
        return self.stat.st_ctime

    def format_created(self, formatter=default_time_format):
        '''Returns creation time formatted

        :param formatter: :func:`time.strftime` format string
            defaults to "%d %b %Y %H:%M:%S"
        '''

        local = time.localtime(self.created)
        return time.strftime(formatter, local)

    @property
    def size(self):
        '''Size in bytes'''

        return self.stat.st_size

    @property
    def size_mb(self):
        '''Get size in megabytes'''

        return self.size * .000001

    @property
    def size_kb(self):
        '''Get size in kilobytes'''

        return self.size * .001


def walk_dn(root, steps=10):
    '''Walk through a directory tree. Similar to os.walk but takes a steps
    parameter to determine walk depth.

    :param root: Directory to walk through
    :param steps: Maximum steps taken through the tree
    :returns: (root, subdirs, files) such that a path can be constructed
    joining root with a subdir or file.
    '''

    root = os.path.normpath(root)
    depth = root.count(os.path.sep)
    max_step = depth + steps
    for root, dirs, files in os.walk(root):
        yield root, dirs, files

        depth = root.count(os.path.sep)
        if depth >= max_step:
            break
