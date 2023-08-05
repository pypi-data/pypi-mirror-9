# -*- coding: utf-8 -*-

import os
import sys
import shutil
from tempfile import mkdtemp
import wanderer.utils as utils
import unittest


class TestUtilities(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = mkdtemp()
        tmp_folders = [
            'walk_tree/subdirc/subdir/a/c',
            'walk_tree/subdirb',
            'walk_tree/subdir',
        ]
        temp_files = ['walk_tree/.wanderer', 'walk_tree/.file']

        for d in tmp_folders:
            os.makedirs(os.path.join(self.tmp_dir, d))

        for f in temp_files:
            path = os.path.join(self.tmp_dir, f)
            with open(os.path.join(self.tmp_dir, f), 'a'):
                os.utime(path, None)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_walk_up(self):
        '''Walk up through directory tree'''
        path = os.path.join(self.tmp_dir, 'walk_tree/subdirc/subdir/a/c')

        for root, subdirs, files in utils.walk_up(path, 5):
            r, s, f = root, subdirs, files

        assert r == os.path.join(self.tmp_dir, 'walk_tree')
        assert s == ['subdir', 'subdirb', 'subdirc']
        assert f == ['.file', '.wanderer']

    def test_walk_dn(self):
        '''Walk down through directory tree'''
        path = os.path.join(self.tmp_dir, 'walk_tree')

        for root, subdirs, files in utils.walk_dn(path, 2):
            r, s, f = root, subdirs, files

        exp_r = os.path.join(self.tmp_dir, 'walk_tree', 'subdirc', 'subdir')
        assert r == exp_r
        assert s == ['a']
        assert f == []


if __name__ == '__main__':
    unittest.main()
