# -*- coding: utf-8 -*-

import wanderer
import wanderer.utils as utils
import os
import shutil
from tempfile import mkdtemp
import unittest


class TestWanderer(unittest.TestCase):

    def setUp(self):
        self.app = wanderer.Wanderer()

    def tearDown(self):
        pass


class TestBootstrap(unittest.TestCase):

    def setUp(self):
        self.temp_dir = mkdtemp()
        self.path = os.path.join(self.temp_dir, 'project')

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_bootstrap(self):
        '''Bootstrap a project'''

        app = wanderer.Wanderer.bootstrap(self.path)

        assert os.path.exists(self.path)
        assert os.path.exists(os.path.join(self.path, '.wanderer'))
        assert os.environ['WA_PROJECT'] == self.path

    def test_fresh_env(self):
        '''Use cls attribute old_env to restore environment'''

        utils.env_set_state(*wanderer.Wanderer.old_env)

        assert 'WA_PROJECT' not in os.environ.data
        assert 'WA_CFG' not in os.environ.data

if __name__ == '__main__':
    unittest.main()
