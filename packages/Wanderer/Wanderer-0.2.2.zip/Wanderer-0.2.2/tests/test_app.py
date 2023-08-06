# -*- coding: utf-8 -*-
'''
Test :class:`Wanderer` main functionality
'''
import os
import shutil
import subprocess
from tempfile import mkdtemp
import unittest

from nose.tools import nottest, raises
from tests import data_path

import wanderer
from wanderer import FilePath, first


@nottest
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

    def test_bootstrap_custom(self):
        '''Bootstrap a project with custom config'''

        app = wanderer.Wanderer.bootstrap(self.project2, self.project2_cfg)

        self.assertTrue(os.path.exists(self.project2))
        cfg_path = os.path.join(self.project2, '.wanderer')
        self.assertTrue(os.path.exists(cfg_path))
        self.assertEqual(os.environ['WA_PROJECT'], self.project2)

        installed = subprocess.check_output('pip freeze', shell=True)
        self.assertTrue('hotline' in installed)
        self.assertTrue('apptemplate' in installed)
        self.assertTrue('requests' in installed)
        self.assertTrue('mvp' in installed)


class TestWanderer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = mkdtemp()
        cls.path = os.path.join(cls.temp_dir, 'project')
        cls.app = wanderer.Wanderer.bootstrap(cls.path)
        cls.git_addr = 'git+https://github.com/danbradham/apptemplate.git'

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir)

    @nottest
    def test_install(self):
        '''Install a python package'''

        self.app.install(self.git_addr)
        installed = subprocess.check_output('pip freeze', shell=True)
        self.assertTrue('apptemplate' in installed)

    def test_new_asset(self):
        '''New asset'''

        asset = self.app.new_asset(name='cool_asset', cat='characters')
        self.assertEqual(asset.name, 'cool_asset')
        self.assertEqual(asset.cat, 'characters')

        expected = FilePath('$WA_ASSETS/characters/cool_asset').expand()
        self.assertEqual(asset.path.normpath, expected)
        self.assertTrue(asset.path.exists)

    @raises(NameError)
    def test_new_asset_component_exists(self):
        '''Raise NameError if asset component already exists'''

        asset = first(self.app.find_asset(name='cool_asset'))
        model = asset.new_component(name='model')

    def test_new_asset_component(self):
        '''New asset component'''

        asset = first(self.app.find_asset(name='cool_asset'))
        anim = asset.new_component(name='animation')
        self.assertEqual(anim.name, 'animation')

        expected = FilePath('$WA_ASSETS/characters/cool_asset/animation')
        self.assertEqual(anim.path.normpath, expected.expand())
        self.assertTrue(anim.path.exists)

    def test_new_sequence(self):
        '''New sequence'''

        seq = self.app.new_sequence(name='sequence01')
        self.assertEqual(seq.name, 'sequence01')

        expected = FilePath('$WA_SEQUENCES/sequence01').expand()
        self.assertEqual(seq.path.normpath, expected)
        self.assertTrue(seq.path.exists)

    def test_new_shot(self):
        '''New shot'''

        seq = first(self.app.find_sequence(name='sequence01'))
        shot = seq.new_shot(name='shot01')
        self.assertEqual(seq.name, 'sequence01')

        expected = FilePath('$WA_SEQUENCES/sequence01').expand()
        self.assertEqual(seq.path.normpath, expected)
        self.assertTrue(seq.path.exists)

    @raises(NameError)
    def test_new_shot_component_exists(self):
        '''Raise NameError if shot component already exists'''

        shot = first(self.app.find_shot(name='shot01'))
        anim = shot.new_component(name='animation')

    def test_new_shot_component(self):
        '''New shot component'''

        shot = first(self.app.find_shot(name='shot01'))
        abclo = shot.new_component(name='abclayout')
        self.assertEqual(abclo.name, 'abclayout')

        expected = FilePath(
            '$WA_SEQUENCES/sequence01/shot01/abclayout').expand()
        self.assertEqual(abclo.path.normpath, expected)
        self.assertTrue(abclo.path.exists)

    def test_zfind_shot_components(self):
        '''Find shot components'''

        shot = first(self.app.find_shot(name='shot01'))
        components = shot.find_component()

        names = set([c.name for c in components])
        expected = set(['animation', 'compositing', 'layout',
                        'lighting', 'exchange', 'renders'])
        self.assertEqual(expected - names, set(['exchange', 'renders']))

    def test_zfind_asset_components(self):
        '''Find asset components'''

        asset = first(self.app.find_asset(name='cool_asset'))
        components = asset.find_component()

        names = set([c.name for c in components])
        expected = set(['model', 'rig', 'exchange', 'shaders', 'textures'])
        self.assertEqual(expected - names,
                         set(['exchange', 'shaders', 'textures']))

    def test_data_from_path(self):
        '''Get data from a path'''

        path_a = FilePath('$WA_SEQUENCES/sequence01/shot01/animation')
        path_a = path_a.expand().replace('\\', '/')
        path_b = FilePath('$WA_SEQUENCES/sequence01/shot01')
        path_b = path_b.expand().replace('\\', '/')
        path_c = FilePath('$WA_SEQUENCES/sequence01/shot01/stupid/path')
        path_c = path_c.expand().replace('\\', '/')
        path_d = FilePath('$WA_ASSETS/characters/asset01/model/maya/work/'
                          'mdl_asset01.v005.mb')
        path_d = path_d.expand().replace('\\', '/')

        expected_data_a = {
            'sequence': {'name': 'sequence01', 'path': path_a.parent.parent},
            'shot': {'name': 'shot01', 'path': path_a.parent},
            'component': {'name': 'animation', 'path': path_a},
            'project': {'path': self.app.root, 'name': self.app.root.name},
        }

        expected_data_b = {
            'sequence': {'name': 'sequence01', 'path': path_b.parent},
            'shot': {'name': 'shot01', 'path': path_b},
            'project': {'path': self.app.root, 'name': self.app.root.name},
        }

        expected_data_c = {
            'sequence': {'name': 'sequence01',
                         'path': path_c.parent.parent.parent},
            'shot': {'name': 'shot01', 'path': path_c.parent.parent},
            'component': {'name': 'stupid', 'path': path_c.parent},
            'project': {'path': self.app.root, 'name': self.app.root.name},
        }

        expected_data_d = {
            'asset': {'name': 'asset01', 'cat':'characters',
                      'path': path_d.parent.parent.parent.parent},
            'component': {'name': 'model', 'version': '005', 'short': 'mdl',
                          'path': path_d.parent.parent.parent},
            'project': {'path': self.app.root, 'name': self.app.root.name},
        }

        ctx_a = self.app._data_from_path(path_a)
        ctx_b = self.app._data_from_path(path_b)
        ctx_c = self.app._data_from_path(path_c)
        ctx_d = self.app._data_from_path(path_d)

        self.assertEqual(ctx_a, expected_data_a)
        self.assertEqual(ctx_b, expected_data_b)
        self.assertEqual(ctx_c, expected_data_c)
        self.assertEqual(ctx_d, expected_data_d)

if __name__ == '__main__':
    unittest.main()
