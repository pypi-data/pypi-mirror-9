# -*- coding: utf-8 -*-
'''
Make file system paths object oriented...
'''

import glob
import fnmatch
import os
import posixpath
import shutil
import time


class alias(object):
    '''Alias descriptor for wrapping os functions'''

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

    def __add__(self, other):
        '''Returns a :class:`FilePath`'''

        return FilePath(super(FilePath, self).__add__(other))

    def __iadd__(self, other):
        '''Adds to self and returns'''

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
    normcase = alias(os.path.normcase, returns_typ=True)
    normpath = alias(os.path.normpath, returns_typ=True)
    relpath = alias(os.path.relpath, returns_typ=True)
    realpath = alias(os.path.realpath, returns_typ=True)

    def expanduser(self):
        '''Expand user vars and return new :class:`FilePath`'''

        return FilePath(os.path.expanduser(self))

    def expandvars(self):
        '''Expand env vars and return new :class:`FilePath`'''

        return FilePath(os.path.expandvars(self))

    def expand(self):
        '''Expand user vars and env vars then normalize'''

        return self.expanduser().expandvars().normpath

    def samestat(self, other):
        '''On unix systems, returns true if the two files have the same stat'''

        return os.path.samestat(self.stat, other.stat)

    def glob(self, pattern):
        '''Glob relative to :class:`FilePath`'''
        globbed = glob.glob(self.join(pattern))
        for p in globbed:
            yield FilePath(p)

    def join(self, *args):
        '''wraps :func:`os.path.join`'''

        return FilePath(os.path.join(self, *args)).normpath

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

    def splitpath(self):
        '''wraps :func:`os.path.split`'''

        head, tail = os.path.split(self)

        return FilePath(head), tail

    def splitext(self):
        name, ext = os.path.splitext(self)

        return FilePath(name), ext

    def replace(self, *args, **kwargs):
        '''Wraps replace to return a FilePath object instead of a str object'''

        return FilePath(super(FilePath, self).replace(*args, **kwargs))

    def move(self, destination):
        '''Move directory or file to another location.'''

        if not FilePath(destination).exists:
            shutil.move(self, destination)

        self = FilePath(destination)
        return self

    def copy(self, destination):
        '''Copy file or folder to another location.'''
        dest = FilePath(destination)

        if not dest.exists:

            if self.isdir:
                shutil.copytree(self, dest)
            else:
                shutil.copy2(self, dest)

            return dest

        raise OSError('{0} already exists'.format(dest))

    @property
    def ext(self):
        return self.splitext()[-1]

    @property
    def name(self):
        return str(self.basename.splitext()[0])

    @property
    def parent(self):
        return self.dirname

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
