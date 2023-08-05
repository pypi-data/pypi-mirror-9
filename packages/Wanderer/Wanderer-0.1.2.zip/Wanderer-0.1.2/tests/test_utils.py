# -*- coding: utf-8 -*-

import os
import sys
import shutil
from tempfile import mkdtemp
import wanderer.utils as utils
import unittest


OLD_ENV = utils.env_get_state()


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


class TestEnvUtils(unittest.TestCase):
    '''Test all environment utilities.'''

    def setUp(self):

        self.tmp_dir = mkdtemp()
        self.tmp_folders = [
            'Python/Lib/site-packages',
            'Python/Lib/site-packages/awesome.egg',
            'Python/Lib/site-packages/another.egg',
        ]

        for d in self.tmp_folders:
            os.makedirs(os.path.join(self.tmp_dir, d))

        self.env = {
            'WA_PROJECT': 'a/cool/project/path',
            'WA_OS': 'OPERATINGSYSTEM',
            'PATH': ['a/cool/path', 'a/second/cool/path'],
            'PYTHONPATH': [os.path.join(self.tmp_dir, self.tmp_folders[0])],
        }

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_env_from_dict(self):
        '''Test setting environment from dictionary'''

        utils.env_from_dict(self.env)

        print '\n'.join(sys.path)

        assert 'a/cool/project/path' in os.environ['WA_PROJECT']
        assert 'OPERATINGSYSTEM' in os.environ['WA_OS']
        assert 'a/cool/path' in os.environ['PATH']
        assert os.path.join(self.tmp_dir, self.tmp_folders[0]) in sys.path
        assert 'awesome.egg' in ';'.join(sys.path)
        assert 'another.egg' in ';'.join(sys.path)

    def test_env_set_state(self):
        '''Test environment restoration.'''

        utils.env_set_state(*OLD_ENV)

        assert '/a/cool/project/path' not in os.environ.get('WA_PROJECT', '')
        assert 'OPERATINGSYSTEM' not in os.environ.get('WA_OS', '')
        assert 'a/cool/path' not in os.environ.get('PATH', '')
        assert os.path.join(self.tmp_dir, self.tmp_folders[0]) not in sys.path
        assert 'awesome.egg' not in ';'.join(sys.path)
        assert 'another.egg' not in ';'.join(sys.path)

if __name__ == '__main__':
    unittest.main()
