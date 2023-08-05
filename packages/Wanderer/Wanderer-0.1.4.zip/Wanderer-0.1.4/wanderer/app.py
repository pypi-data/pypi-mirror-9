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
from functools import partial
from . import utils, env
from .config import Config

env.save() # Store a clean environment
package_path = partial(os.path.join, os.path.dirname(__file__))


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
        'debug': False,
    }

    def __init__(self):
        self.config = Config(**self.defaults)

        self.root = os.environ.setdefault('WA_PROJECT', '')
        cfg_path = os.environ.setdefault('WA_CFG', expanduser('~/.wanderer'))

        if not os.path.exists(cfg_path):
            shutil.copytree(package_path('.wanderer'), cfg_path)

        self.config.from_env('WA_CFG')

        self.setup_env(self.config['ENV'])

    def setup_env(self, d):
        '''Used for setting environments configured in your wanderer config.
        ::

            wanderer.setup_env(wanderer.config['ENV'])

        :param d: Dictionary that defines an environment.'''

        env.from_dict(d)

    def install(self, package, os_specific=False):
        '''A wrapper around python pip allowing you to install packages
        dirctly to a wanderer project::

            app.install('hotline')

        Installs a package named **hotline** to the following python site in
        your project::

            $WA_PROJECT/.wanderer/environ/Python/common

        This works fine if you know that the package you are installing is a
        pure python package. If you are installing a package with lots of
        dependencies or a c extension component, use the --os-specific option.
        This will install your package to one of the following locations.

         * $WA_PROJECT/.wanderer/environ/Python/linux
         * $WA_PROJECT/.wanderer/environ/Python/osx
         * $WA_PROJECT/.wanderer/environ/Python/win

        Let's install **hotline** again, but this time from it's github
        repository::

            app.install('git+git@github.com:danbradham/hotline.git')

        :param package: Name of the package or git repo to install
        :param os_specific: Install to your projects os specific py site?
        '''

        cmd = 'pip install -q --install-option="--prefix={prefix}" {package}'

        if os_specific:
            project_pysite = '$WA_CFG/environ/Python/$WA_OS'
        else:
            project_pysite = '$WA_CFG/environ/Python/common'

        prefix = os.path.expandvars(project_pysite)
        cmd = cmd.format(package=package, prefix=prefix)

        p = subprocess.Popen(cmd, shell=True)
        p.wait()

    def uninstall(self, package):
        '''A wrapper around python pip allowing you to uninstall packages
        from a wanderer project::

            app.uninstall('hotline')

        :param package: Name of the package to uninstall
        '''

        cmd = 'pip uninstall {package}'.format(package=package)
        p = subprocess.Popen(cmd, shell=True)
        p.wait()

    def launch(self, app):
        '''Used to launch a CG application in a Wanderer project environment.
        ::

            app.launch('maya')

        :param app: Name of application to launch. This is used to pull in an
        app_path and env defined in your configuration.
        '''

        app_cfg = self.config['APPLICATIONS'][app.lower()]
        self.setup_env(app_cfg['ENV'])
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

        tmpl = self.config['TEMPLATES'][template]
        filepath = tmpl.format(**self.context.__dict__)
        return os.path.abspath(os.path.join(self.root, filepath))

    @classmethod
    def bootstrap(cls, path, config=None):
        '''Bootstrap a new project.

        :param path: Full path of new project
        :param config: Full path to a configuration to use defaults to the
        config folder pacakged with wanderer
        :returns: Wanderer instance with context set to new project'''

        if not config:
            project_template = package_path('.wanderer/templates/project')
            config_template = package_path('.wanderer')
        else:
            project_template = os.path.join(config, 'templates', 'project')
            config_template = config

        shutil.copytree(project_template, path)
        shutil.copytree(config_template, os.path.join(path, '.wanderer'))

        return cls.from_path(path)

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
