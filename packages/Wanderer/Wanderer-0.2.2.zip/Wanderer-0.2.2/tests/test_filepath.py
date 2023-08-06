# -*- coding: utf-8 -*-
'''
Test :class:`FilePath`
'''

import os
import shutil
import sys
from tempfile import mkdtemp
import unittest

#Under Testing
from wanderer.filepath import FilePath

platform = sys.platform.rstrip('1234567890').lower()

class TestFilePath(unittest.TestCase):
    '''Test all FilePath functionality.'''

    def test_repr(self):
        '''FilePath.__repr__'''

        p = FilePath('/a/b/c')
        self.assertEqual(repr(p), "FilePath('/a/b/c')")

    def test_eq_ne(self):
        '''FilePath.__eq__, FilePath.__ne__'''

        p1 = FilePath('c:/a/b/c')
        p2 = FilePath('C:\\a\\b\\c')
        self.assertNotEqual(p1, p2)

        p3 = 'c:/a/b/c'
        self.assertEqual(p1, p3)

        p4 = 'C:\\a\\b\\c'
        self.assertNotEqual(p1, p4)

    def test_add(self):
        '''FilePath.__add__, FilePath.__iadd__'''

        p1 = FilePath('a/b/c')
        p2 = FilePath('d/e/f')
        p3 = p1 + p2
        self.assertEqual(p3, 'a/b/cd/e/f')
        self.assertTrue(isinstance(p3, FilePath))

        p1 += p2
        self.assertEqual(p1, 'a/b/cd/e/f')
        self.assertTrue(isinstance(p1, FilePath))

    def test_join(self):
        '''FilePath.join'''

        p1 = FilePath('a')
        p2 = FilePath('b')

        self.assertEqual(p1.join(p2), os.path.join('a', 'b'))
        self.assertEqual(p1.join('b'), p1.join(p2))
        self.assertTrue(isinstance(p1.join(p2), FilePath))

    def test_glob(self):
        '''FilePath.glob'''

        #Set up some test paths
        tmpdir = FilePath(mkdtemp())
        folders = [
            'assets/characters/char_a',
            'assets/characters/char_b',
            'assets/characters/char_c',
            'assets/characters/char_a/model/work/',
        ]
        files = [
            'assets/characters/char_a/model/work/my_file.txt'
        ]

        for f in folders:
            os.makedirs(tmpdir.join(f))

        for f in files:
            pth = tmpdir.join(f)
            with open(pth, 'a'):
                os.utime(pth, None)

        g1 = list(tmpdir.glob('assets/*/*'))
        tests = [tmpdir.join(f) in g1 for f in folders[:-1]]
        self.assertTrue(all(tests))

        g2 = list(tmpdir.glob('assets/*/char_a/model/*/*.txt'))
        self.assertTrue(tmpdir.join(files[0]) in g2)

        shutil.rmtree(tmpdir)

    def test_properties(self):
        '''Filepath.name'''

        p1 = FilePath('/root/parent/name.ext')
        self.assertEqual(p1.ext, '.ext')
        self.assertEqual(p1.name, 'name')
        self.assertEqual(p1.parent, FilePath('/root/parent'))
        self.assertEqual(p1.parent.parent, FilePath('/root'))

        p2 = FilePath('/root/parent/name')
        self.assertEqual(p2.ext, '')
        self.assertEqual(p2.name, 'name')
        self.assertEqual(p2.parent, FilePath('/root/parent'))
        self.assertEqual(p2.parent.parent, FilePath('/root'))

        p3 = FilePath('/root/parent/name/')
        self.assertEqual(p3.ext, '')
        self.assertEqual(p3.name, '')
        self.assertEqual(p3.parent, FilePath('/root/parent/name'))
        self.assertEqual(p3.parent.parent, FilePath('/root/parent'))

        try:
            p1.stat
        except:
            pass # OK - Expected
        else:
            raise Exception('Stat on non-existant path should raise an exc')
