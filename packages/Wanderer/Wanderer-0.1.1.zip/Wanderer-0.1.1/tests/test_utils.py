# -*- coding: utf-8 -*-

import os
import shutil
from tempfile import mkdtemp
import wanderer.utils as wutils
import unittest



class TestUtilities(unittest.TestCase):

    def setUp(self):
        self.temp_dir = mkdtemp()
        temp_folders = [
            'walk_tree/subdirc/subdir/a/c',
            'walk_tree/subdirb',
            'walk_tree/subdir',
        ]
        temp_files = ['walk_tree/.wanderer', 'walk_tree/.file']

        for d in temp_folders:
            os.makedirs(os.path.join(self.temp_dir, d))

        for f in temp_files:
            path = os.path.join(self.temp_dir, f)
            with open(os.path.join(self.temp_dir, f), 'a'):
                os.utime(path, None)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_walk_up(self):
        '''Walk up through test folders structure'''
        path = os.path.join(self.temp_dir, 'walk_tree/subdirc/subdir/a/c')

        for root, subdirs, files in wutils.walk_up(path, 5):
            r, s, f = root, subdirs, files

        assert r == os.path.join(self.temp_dir, 'walk_tree')
        assert s == ['subdir', 'subdirb', 'subdirc']
        assert f == ['.file', '.wanderer']

if __name__ == '__main__':
    unittest.main()
