#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools
import os
import sys
import wanderer

if sys.argv[-1] == 'cheeseit!':
    os.system('python setup.py sdist upload')
    sys.exit()

elif sys.argv[-1] == 'testit!':
    os.system('python setup.py sdist upload -r test')
    sys.exit()

with open("README.rst") as f:
    readme = f.read()

setuptools.setup(
    name=wanderer.__title__,
    version=wanderer.__version__,
    description=wanderer.__description__,
    long_description=readme,
    author=wanderer.__author__,
    author_email=wanderer.__email__,
    url=wanderer.__url__,
    license=wanderer.__license__,
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ),
    entry_points='''
        [console_scripts]
        wanderer=wanderer.cli:main
    ''',
)
