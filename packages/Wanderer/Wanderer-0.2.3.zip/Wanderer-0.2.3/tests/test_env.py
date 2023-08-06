# -*- coding: utf-8 -*-

import os
import sys
import shutil
from tempfile import mkdtemp
import wanderer.env as env
import unittest


OLD_ENV = env._get_state()


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

        env.from_dict(self.env)

        self.assertTrue('a/cool/project/path' in os.environ['WA_PROJECT'])
        self.assertTrue('OPERATINGSYSTEM' in os.environ['WA_OS'])
        self.assertTrue('a/cool/path' in os.environ['PATH'])
        self.assertTrue(
            os.path.join(self.tmp_dir, self.tmp_folders[0]) in sys.path)
        self.assertTrue('awesome.egg' in ';'.join(sys.path))
        self.assertTrue('another.egg' in ';'.join(sys.path))

    def test_env_set_state(self):
        '''Test environment restoration.'''

        env._set_state(*OLD_ENV)

        self.assertFalse(
            '/a/cool/project/path' in os.environ.get('WA_PROJECT', ''))
        self.assertFalse('a/cool/path' in os.environ.get('PATH', ''))
        self.assertFalse(
            os.path.join(self.tmp_dir, self.tmp_folders[0]) in sys.path)
        self.assertFalse('awesome.egg' in ';'.join(sys.path))
        self.assertFalse('another.egg' in ';'.join(sys.path))
        self.assertTrue('WA_CLEAN_ENV' in os.environ)
        self.assertTrue('WA_OS' in os.environ)
