# -*- coding: utf-8 -*-
'''
Test :class:`Wanderer` main functionality
'''
import wanderer
import wanderer.utils as utils
import os
import shutil
import subprocess
from tempfile import mkdtemp
import unittest
from tests import data_path


class TestBootstrap(unittest.TestCase):

    def setUp(self):
        self.temp_dir = mkdtemp()
        self.project = os.path.join(self.temp_dir, 'project')
        self.project2_cfg = data_path('bootstrap_cfg')
        self.project2 = os.path.join(self.temp_dir, 'project2')

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_bootstrap(self):
        '''Bootstrap a project from the default configuration'''

        app = wanderer.Wanderer.bootstrap(self.project)

        self.assertTrue(os.path.exists(self.project))
        self.assertTrue(os.path.exists(os.path.join(self.project, '.wanderer')))
        self.assertEqual(os.environ['WA_PROJECT'], self.project)

    def test_bootstrap_installs(self):
        '''Bootstrap a project with several entires in BOOSTRAP/INSTALLS'''

        app = wanderer.Wanderer.bootstrap(self.project2, self.project2_cfg)

        self.assertTrue(os.path.exists(self.project2))
        cfg_path = os.path.join(self.project2, '.wanderer')
        self.assertTrue(os.path.exists(cfg_path))
        self.assertEqual(os.environ['WA_PROJECT'], self.project2)

        output = subprocess.check_output('pip freeze', shell=True)
        self.assertTrue('hotline' in output)
        self.assertTrue('apptemplate' in output)
        self.assertTrue('requests' in output)
        self.assertTrue('mvp' in output)




class TestWanderer(unittest.TestCase):

    def setUp(self):
        self.temp_dir = mkdtemp()
        self.path = os.path.join(self.temp_dir, 'project')
        self.app = wanderer.Wanderer.bootstrap(self.path)
        self.git_addr = 'git+ssh://git@github.com/danbradham/apptemplate.git'

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_install(self):
        '''Test install python package'''

        self.app.install(self.git_addr)
        install_path = os.path.expandvars(
            '$WA_CFG/environ/python/lib/site-packages/apptemplate')
        self.assertTrue(os.path.exists(install_path))
        import apptemplate


if __name__ == '__main__':
    unittest.main()
