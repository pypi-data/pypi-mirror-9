# -*- coding: utf-8 -*-

import wanderer
import wanderer.utils as utils
import os
import shutil
from tempfile import mkdtemp
import unittest


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


class TestWanderer(unittest.TestCase):

    def setUp(self):
        self.temp_dir = mkdtemp()
        self.path = os.path.join(self.temp_dir, 'project')
        self.app = wanderer.Wanderer.bootstrap(self.path)
        self.git_addr = 'git+ssh://git@github.com/danbradham/apptemplate.git'

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_install_uninstall(self):
        '''Test installing --and uninstalling-- a python package'''

        self.app.install(self.git_addr)
        install_path = os.path.expandvars(
            '$WA_CFG/environ/python/lib/site-packages/apptemplate')
        assert os.path.exists(install_path)
        import apptemplate

        # temporarily disable until i find a solution for testing pip uninstall
        # in a virtualenv
        # self.app.uninstall('apptemplate')
        # assert not os.path.exists(os.path.expandvars(pthchek))


if __name__ == '__main__':
    unittest.main()
