# -*- coding: utf-8 -*-
'''
wanderer.app
============
Contains the main application object :class:`Wanderer`.
'''

import shutil
import os
from os.path import expanduser
import logging
import sys
import subprocess
import tempfile
from wanderer import package_path, WHEEL_INSTALLED
from . import utils, env
from .logging import new_logger
from .config import Config

env.save() # Store a clean environment


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

    def __init__(self):

        self._logger = None

        self.root = os.environ.setdefault('WA_PROJECT', '')
        cfg_path = os.environ.setdefault('WA_CFG', expanduser('~/.wanderer'))
        self.config = Config(**self.defaults)
        self._setup_env(self.config.env) # Setup the environment

        self.logger.info(self.info)

    def __repr__(self):
        return 'Wanderer("{}")'.format(self.root)

    @property
    def logger(self):
        if not self._logger:
            self._logger = new_logger(self)

        return self._logger

    @property
    def info(self):
        info_str = (
            '\n{}\n'
            'Config:         {}\n'
            'Project:        {}\n'
            ).format(repr(self), self.config.root, os.path.basename(self.root))

        return info_str

    def _setup_env(self, d):
        '''.. seealso:: :func:`wanderer.env.from_dict`'''

        self.logger.info('Updating environment.')
        env.from_dict(d)

    def _make_wheel(self, package):
        '''Make a wheel from a wininst or egg so we can install it with pip.

        :param package: Can be a web url or a local path to a win installer
        :returns: (tmp_dir, wheel path) OR None if we failed'''

        self.logger.info('Creating a python wheel from {}'.format(package))

        tmp_dir = tempfile.mkdtemp()

        if package.startswith('http'): # attempt to download
            import urllib2
            try:
                response = urllib2.urlopen(package)
            except urllib2.URLError:
                return

            package = os.path.join(tmp_dir, 'packinstaller.exe')
            with open(package, 'w') as f:
                f.write(response.read())

        # Convert executable to wheel so we can install it with pip
        p = subprocess.Popen('wheel convert {} -d {}'.format(package, tmp_dir))
        p.wait()

        for f in os.listdir(tmp_dir): # search for the wheel
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

        global WHEEL_INSTALLED
        if not WHEEL_INSTALLED: # Ensure we have wheel support
            self.logger.info('wheel package not found: installing now')

            try:
                subprocess.check_call('pip -q install wheel', shell=True)
            except subprocess.CalledProcessError:
                self.logger.exception(
                    'Failed to install wheel, you will not be able to install '
                    'from wininst or egg files')

            WHEEL_INSTALLED = True

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

        pip_opts = ['--install-option="{}"'.format(opt) for opt in inst_opts]

        cmd = ['pip', '-q', 'install']
        cmd.extend(pip_opts)
        cmd.append(package)

        try:
            subprocess.check_call(' '.join(cmd), shell=True)
        except subprocess.CalledProcessError:
            self.logger.exception('Failed to install ' + package)


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
        p = subprocess.Popen(
            os.path.abspath(app_cfg['PATH'][os.environ['WA_OS']]),
            shell=True,
            env=os.environ.copy(),
            cwd=os.path.abspath(self.root))
        return p.pid

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
        return os.path.abspath(os.path.join(self.root, filepath))

    @classmethod
    def bootstrap(cls, path, config=None):
        '''Bootstrap a new project.

        :param path: Full path of new project
        :param config: Full path to a configuration to use defaults to the
        config folder pacakged with wanderer
        :returns: Wanderer instance with context set to new project'''

        tmp_dir = None

        if not config:
            config_template = package_path('.wanderer')
            project_template = package_path('.wanderer/templates/project')
        else:
            if config.startswith('git'): # Clone the config git repo
                tmp_dir = tempfile.mkdtemp()
                config_template = os.path.join(tmp_dir, '.wanderer')
                try:
                    subprocess.check_call(
                        'git clone {} {}'.format(config, config_template))
                except subprocess.CalledProcessError:
                    raise
            else:
                config_template = config
            project_template = os.path.join(
                config_template, 'templates/project')

        shutil.copytree(project_template, path)
        shutil.copytree(config_template, os.path.join(path, '.wanderer'))

        new_wanderer = cls.from_path(path) # Get the new wanderer

        try:
            packages = new_wanderer.config.bootstrap['INSTALLS']
            for package in packages:
                try:
                    __import__(package)
                except ImportError:
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

        project = None
        for root, subdirs, files in utils.walk_up(path):
            if '.wanderer' in subdirs:
                project = root
                break

        if project:
            if 'WA_PROJECT' in os.environ:
                env.restore()
            os.environ['WA_PROJECT'] = project
            os.environ['WA_CFG'] = os.path.join(project, '.wanderer')

        return cls()
