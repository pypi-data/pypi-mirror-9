# -*- coding: utf-8 -*-
'''
Make file system paths object oriented...
'''

import os
import posixpath
import time


class pathalias(object):

    def __init__(self, method, returns_path=False):
        self.method = method
        self.returns_path = returns_path

    def __get__(self, obj, typ=None):
        val = self.method(obj)
        if self.returns_path:
            return typ(val)
        return val


class FilePath(str):

    default_time_format = '%d %b %Y %H:%M:%S'

    def __repr__(self):
        return "FilePath('{}')".format(self)

    def __eq__(self, other):
        if isinstance(other, FilePath):
            return self.normpath == other.normpath
        return self == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        '''Uses :func:`os.path.join` and returns a new :class:`FilePath`'''

        return FilePath(self + other)

    def __iadd__(self, other):
        '''Uses :func:`os.path.join` in place replacing the current
        :class:`FilePath` with the result.'''

        self[:] = FilePath(self + other)
        return self

    exists = pathalias(os.path.exists)
    isfile = pathalias(os.path.isfile)
    isdir = pathalias(os.path.isdir)
    islink = pathalias(os.path.islink)
    basename = pathalias(os.path.basename, returns_path=True)
    dirname = pathalias(os.path.dirname, returns_path=True)
    abspath = pathalias(os.path.abspath, returns_path=True)
    normpath = pathalias(os.path.normpath, returns_path=True)
    realpath = pathalias(os.path.realpath, returns_path=True)

    def join(self, *args):
        '''wraps :func:`os.path.join`'''

        return FilePath(os.path.join(self, *args))

    def walk(self):
        '''Walks down through a directory.

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
