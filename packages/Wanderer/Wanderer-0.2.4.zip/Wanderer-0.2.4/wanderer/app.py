# -*- coding: utf-8 -*-
'''
wanderer.app
============
Contains the main application object :class:`Wanderer`.
'''

from __future__ import absolute_import
from collections import defaultdict
import shutil
import os
from os.path import expanduser
import logging
import re
import sys
import subprocess
import tempfile
from wanderer import package_path
from . import env
from .utils import find_project
from .config import Config
from .filepath import FilePath
from .formatters import format_regex, format_glob
import logging
from logging import getLogger, StreamHandler, FileHandler, Formatter
from .models import *

env.save() # Store a clean environment
STANDARD_FORMAT = '\n<%(asctime)s>[%(levelname)s %(module)s] %(message)s'
DEBUG_FORMAT = (
    '\n<%(asctime)s>[%(levelname)s %(module)s](%(funcName)s %(lineno)d)\n'
    '%(message)s\n'
)


class Context(object):
    '''All of the models that make up the current state of Wanderer'''

    def __init__(self, project=None, asset=None, sequence=None, shot=None,
                 component=None):

        self.project = project
        self.asset = asset
        self.sequence = sequence
        self.shot = shot
        self.component = component


class Wanderer(object):
    '''Handles all things Wanderer. The most typical way of getting a
    :class:`Wanderer` app instance is by path::

        from wanderer import Wanderer
        app = Wanderer.from_path('project/path')

    When inside an application that already has a Wanderer environment setup
    simply create an instance, and it will pull in the proper config using the
    projects environment variables::

        app = Wanderer()

    :ivar config: A :class:`Config` object referencing a project config
    :ivar root: points to your project root directory'''

    defaults = {
        'DEBUG': False,
    }

    _instance = None

    def __init__(self):

        self._logger = None

        self.root = FilePath(os.environ.setdefault('WA_PROJECT', ''))
        cfg_path = FilePath(
            os.environ.setdefault('WA_CFG', expanduser('~/.wanderer')))
        self.config = Config(**self.defaults)
        self._setup_env(self.config.env) # Setup the environment

        self.logger.info(self.info)

    def __repr__(self):
        return 'Wanderer("{0}")'.format(self.root)

    def _new_logger(self):
        '''Create a new logger for a Wanderer instance.'''

        sh = StreamHandler()
        if self.config.debug:
            sh.setLevel(logging.DEBUG)
            sh.setFormatter(Formatter(DEBUG_FORMAT))
        else:
            sh.setFormatter(Formatter(STANDARD_FORMAT))

        logger = getLogger(self.root.basename)
        logger.addHandler(sh)

        return logger

    @property
    def logger(self):
        if not self._logger:
            self._logger = self._new_logger()

        return self._logger

    @property
    def info(self):
        info_str  = '\n' + ' Wanderer Context '.center(80, '-')
        info_str += '\n'
        info_str += '\n{0}\n'.format(repr(self))
        info_str += 'Project:    {0}\n'.format(self.root.name)
        info_str += 'Config:     {0}\n'.format(self.config.root)
        info_str += '\n'
        info_str += '{0:->80}\n'.format('-')

        return info_str

    def _setup_env(self, d):
        '''.. seealso:: :func:`wanderer.env.from_dict`'''

        self.logger.info('Updating environment.')
        env.from_dict(d)

    def _make_wheel(self, package):
        '''Make a wheel from a wininst or egg so we can install it with pip.

        :param package: Can be a web url or a local path to a win installer
        :returns: (tmp_dir, wheel path) OR None if we failed'''

        self.logger.info('Creating a python wheel from {0}'.format(package))

        try: # Make sure we have wheel support
            import wheel
        except ImportError:
            self.logger.info('wheel package not found: installing now')

            try:
                subprocess.check_call('pip -q install wheel', shell=True)
            except subprocess.CalledProcessError:
                self.logger.exception(
                    'Failed to install wheel, you will not be able to install '
                    'from wininst or egg files')

        tmp_dir = FilePath(tempfile.mkdtemp())

        if package.startswith('http'): # attempt to download
            import urllib2
            try:
                response = urllib2.urlopen(package)
            except urllib2.URLError:
                return

            package = tmp_dir.join('packinstaller.exe')
            with open(package, 'w') as f:
                f.write(response.read())

        # Convert executable to wheel so we can install it with pip
        wheel_cmd = 'wheel convert {0} -d {1}'.format(package, tmp_dir)

        try:
            subprocess.check_call(wheel_cmd)
        except subprocess.CalledProcessError:
            self.logger.exception('Failed to install ' + package)
            return

        for f in tmp_dir.listdir: # search for the wheel
            if f.endswith('.whl'):
                return tmp_dir, f

        return

    def install(self, package):
        '''A wrapper around python pip allowing you to install packages
        dirctly to a wanderer project::

            app.install('hotline')

        Installs a package named **hotline** to the following python site in
        your project::

            $WA_PROJECT/.wanderer/environ/python

        Let's install **hotline** again, but this time from it's github
        repository::

            app.install('git+git@github.com:danbradham/hotline.git')

        :param package: Name of the package or git repo to install
        '''

        self.logger.info('installing ' + package)

        tmp_dir = None

        if package.endswith('.exe') or package.endswith('.egg'):
            # create a wheel in a temp directory
            try:
                tmp_dir, package = _make_wheel(package)
            except TypeError:
                self.logger.exception('Failed to download package')

        inst_opts = [
            '--prefix=$WA_CFG/environ/python',
            '--install-purelib=$WA_CFG/environ/python/lib/site-packages',
            '--install-platlib=$WA_CFG/environ/python/lib/$WA_OS',
            '--install-scripts=$WA_CFG/environ/python/scripts',
            '--install-data=$WA_CFG/environ/python/data',
        ]

        pip_opts = ['--install-option="{0}"'.format(opt) for opt in inst_opts]

        cmd = ['pip', '-q', 'install']
        cmd.extend(pip_opts)
        cmd.append(package)

        try:
            subprocess.check_call(' '.join(cmd), shell=True)
        except subprocess.CalledProcessError:
            self.logger.exception('Failed to install ' + package)
        finally:
            if tmp_dir: # clean up temporary files
                shutil.rmtree(tmp_dir)

    def uninstall(self, package):
        '''A wrapper around python pip allowing you to uninstall packages
        from a wanderer project::

            app.uninstall('hotline')

        :param package: Name of the package to uninstall
        '''

        self.logger.info('uninstalling ' + package)

        cmd = 'pip -q uninstall {package}'.format(package=package)
        try:
            subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError:
            self.logger.exception('Failed to uninstall ' + package)

    def launch(self, app_name):
        '''Used to launch a CG application in a Wanderer project environment.
        ::

            app.launch('maya')

        :param app_name: Name of application to launch. Used to pull in an
            app_path and env defined in your configuration.
        '''

        self.logger.info('launching ' + app_name)

        app_cfg = self.config.applications[app_name.lower()]
        self._setup_env(app_cfg['ENV'])
        app_path = FilePath(app_cfg['PATH'][os.environ['WA_OS']])

        p = subprocess.Popen(
            app_path.abspath,
            shell=True,
            env=os.environ.copy(),
            cwd=self.root.abspath)
        return p.pid

    def _data_from_path(self, path):
        '''Extract the most data possible from a given path using all
        configured templates to perform the search.

        :param path: Path to extract data from
        :returns: Dict grouped by object data'''

        path = FilePath(path).replace('\\', '/')

        if not self.root.replace('\\', '/') in path:
            raise LookupError('Path resides outside of current apps root')

        templates = self.config.templates

        best_match = None
        for name, template in templates.iteritems():
            parts = template.replace('\\', '/').split('/')
            while parts:
                tmpl = '/'.join(parts) + '(/|$)'
                pattern = re.compile(format_regex(tmpl)) # template to regex
                m = pattern.search(path)
                if m:
                    data = m.groupdict()
                    if not best_match or len(data) > len(best_match):
                        best_match = data
                        break
                parts.pop()

        if not best_match:
            raise RuntimeError('Could not find an appropriate context.')

        ctx_data = defaultdict(dict)
        for k, v in best_match.iteritems(): # Group data by prefix
            name, attr = k.split('_')
            ctx_data[name][attr] = v

        for k, v in ctx_data.iteritems(): # Get path to each data section
            token = v.get('name', None)
            if token:
                v['path'] = FilePath(path.split(token)[0] + token)

        ctx_data['project']['name'] = self.root.name
        ctx_data['project']['path'] = self.root

        return ctx_data

    def context_from_path(self, path):
        '''Get the best possible context from a given path.

        :param path: Path to generate context from
        :returns: :class:`Context` instance'''

        from . import models

        ctx_data = self._data_from_path(path)

        models = {}
        project_data = ctx_data.get('project', None)
        asset_data = ctx_data.get('asset', None)
        seq_data = ctx_data.get('shot', None)
        shot_data = ctx_data.get('shot', None)
        comp_data = ctx_data.get('component', None)

        project = Project(app=self, path=project_data['path'])
        models['project'] = project
        if asset_data:
            ass = Asset(app=self, path=asset_data['path'], parent=project)
            models['asset'] = ass
        if seq_data:
            seq = Sequence(app=self, path=seq_data['path'], parent=project)
            models['sequence'] = seq
        if shot_data:
            sho = Shot(app=self, path=shot_data['path'], parent=seq)
            models['shot'] = sho
        if comp_data:
            parent = 'asset' if 'asset' in models else 'shot'
            comp = Component(app=self, path=comp_data['path'], parent=parent)
            models['component'] = comp

        return Context(**models)

    def find_asset(self, name='*', cat='*'):
        '''Search for a matching model'''

        assets_path = FilePath('$WA_ASSETS').expand()

        for ass in assets_path.glob('{0}/{1}'.format(cat, name)):
            yield Asset(app=self, path=ass)

    def find_sequence(self, name='*'):

        sequences_path = FilePath('$WA_SEQUENCES').expand()

        for seq in sequences_path.glob('{0}'.format(name)):
            yield Sequence(app=self, path=seq)

    def find_shot(self, name='*', sequence='*'):

        sequences_path = FilePath('$WA_SEQUENCES').expand()

        for sh in sequences_path.glob('{0}/{1}'.format(sequence, name)):
            parent = Sequence(app=self, path=sh.parent)
            yield Shot(app=self, path=sh, parent=parent)

    def find_component(self, name='*', asset=None, cat='*',
                       shot=None, sequence='*'):

        assets_path = FilePath('$WA_ASSETS').expand()
        sequences_path = FilePath('$WA_SEQUENCES').expand()

        if asset:
            ass = list(self.find_asset(name=asset, cat=cat))
            if ass:
                components = ass[0].find_component(name=name)
                for c in components:
                    yield c
        elif shot:
            shot = list(self.find_shot(name=shot, sequence=sequence))
            if shot:
                components = shot[0].find_component(name=name)
                for c in components:
                    yield c
        else:
            for ass in self.find_asset(cat=cat):
                for c in ass.find_component(name=name):
                    yield c
            for sh in self.find_shot(sequence=sequence):
                for c in sh.find_component(name=name):
                    yield c

    def new_asset(self, cat, name, template=None):
        '''Create a new asset!

        :param cat: Category of asset
        :param name: Name of asset
        :returns: :class:`Asset`'''

        self.logger.info('Creating a new {0} named {1}'.format(cat, name))

        path = FilePath('$WA_ASSETS/{0}/{1}'.format(cat, name)).expand()
        project = Project(app=self, path=self.root)

        return Asset.new(app=self, path=path,
                         parent=project, template=template)

    def new_sequence(self, name, template=None):
        '''Create a sequence

        :param name: Name of sequence
        :returns: :class:`Sequence`'''

        self.logger.info('Creating a new sequence named {0}'.format(name))

        path = FilePath('$WA_SEQUENCES/{0}'.format(name)).expand()
        project = Project(app=self, path=self.root)

        return Sequence.new(app=self, path=path,
                            parent=project, template=template)

    def get_template_dir(self, template):
        '''Get the path to a template folder tree stored in your projects
        .wanderer/templates folder.

        :param template: Name of the template
        :returns: Absolute path to the template folder'''

        return self.config.relative_path('templates/', template)

    def get_template(self, template):
        '''Get a template path from your projects config formatted using the
        current context.
        :returns: Formatted path to a configured path.'''

        tmpl = self.config.templates[template]
        filepath = tmpl.format(**self.context.__dict__)
        return self.root.join(filepath).abspath

    @classmethod
    def bootstrap(cls, path, config=None):
        '''Bootstrap a new project.

        :param path: Full path of new project
        :param config: Full path to a configuration to use defaults to the
        config folder pacakged with wanderer
        :returns: Wanderer instance with context set to new project'''

        path = FilePath(path).expand()

        if path.exists:
            raise OSError('Project path already exists try another location.')

        tmp_dir = None

        if not config:
            config_template = package_path('.wanderer')
            project_template = package_path('.wanderer/templates/project')
        else:
            if config.startswith('git'): # Clone the config git repo
                tmp_dir = FilePath(tempfile.mkdtemp())
                config_template = tmp_dir.join('.wanderer')
                try:
                    subprocess.check_call(
                        'git clone {0} {1}'.format(config, config_template))
                except subprocess.CalledProcessError:
                    raise
            else:
                config_template = FilePath(config).expand()
            project_template = config_template.join('templates/project')

        project_template.copy(path)
        config_template.copy(path.join('.wanderer'))

        new_wanderer = cls.from_path(path) # Get the new wanderer

        try:
            packages = new_wanderer.config.bootstrap['INSTALLS']
            for package in packages:
                new_wanderer.install(package)
        except KeyError, TypeError:
            pass # Didn't find the INSTALLS section of the BOOTSTRAP config

        if tmp_dir:
            shutil.rmtree(tmp_dir)

        return new_wanderer

    @classmethod
    def from_path(cls, path):
        '''Search the specified path for a wanderer project setting the
        necessary environment variables in the process.

        :param path: Search path
        :returns: :class:`Wanderer` instance
        '''

        project = find_project(path)

        if project:
            if 'WA_PROJECT' in os.environ:
                env.restore()
            os.environ['WA_PROJECT'] = project
            os.environ['WA_CFG'] = project.join('.wanderer')

        cls._instance = cls()

        return cls._instance
