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

        self.assertIn('a/cool/project/path', os.environ['WA_PROJECT'])
        self.assertIn('OPERATINGSYSTEM', os.environ['WA_OS'])
        self.assertIn('a/cool/path', os.environ['PATH'])
        self.assertIn(
            os.path.join(self.tmp_dir, self.tmp_folders[0]), sys.path)
        self.assertIn('awesome.egg', ';'.join(sys.path))
        self.assertIn('another.egg', ';'.join(sys.path))

    def test_env_set_state(self):
        '''Test environment restoration.'''

        env._set_state(*OLD_ENV)

        self.assertNotIn(
            '/a/cool/project/path', os.environ.get('WA_PROJECT', ''))
        self.assertNotIn('a/cool/path', os.environ.get('PATH', ''))
        self.assertNotIn(
            os.path.join(self.tmp_dir, self.tmp_folders[0]), sys.path)
        self.assertNotIn('awesome.egg', ';'.join(sys.path))
        self.assertNotIn('another.egg', ';'.join(sys.path))
        self.assertIn('WA_CLEAN_ENV', os.environ)
        self.assertIn('WA_OS', os.environ)
