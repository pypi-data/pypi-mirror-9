#!/usr/bin/env python3
'''
BenchExec is a framework for reliable benchmarking.
This file is part of BenchExec.

Copyright (C) 2007-2015  Dirk Beyer
All rights reserved.

Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import os
import re
from setuptools import setup

# Links for documentation on how to build and use Python packages:
# http://python-packaging-user-guide.readthedocs.org/en/latest/
# http://gehrcke.de/2014/02/distributing-a-python-command-line-application/
# http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/
# https://pythonhosted.org/setuptools/setuptools.html
# https://docs.python.org/3/distutils/index.html

# determine version (more robust than importing benchexec)
# c.f. http://gehrcke.de/2014/02/distributing-a-python-command-line-application/
version = re.search(
    '^__version__\s*=\s*\'(.*)\'',
    open('benchexec/__init__.py').read(),
    re.M
    ).group(1)

# Get the long description from the relevant file
readme = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md')
try:
    import pypandoc
    long_description = pypandoc.convert(readme, 'rst', format='markdown_github-hard_line_breaks')
except (IOError, ImportError):
    with open(readme, encoding='utf-8') as f:
        long_description = f.read()

setup(
    name = 'BenchExec',
    version = version,
    author = 'Dirk Beyer',
    description = ('A Framework for Reliable Benchmarking and Resource Measurement.'),
    long_description = long_description,
    url = 'https://github.com/dbeyer/benchexec/',
    license = 'Apache 2.0 License',
    keywords = 'benchmarking resource measurement',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Benchmark',
        ],
    platforms = ['Linux'],

    packages = ['benchexec', 'benchexec.tablegenerator', 'benchexec.tools'],
    package_data = {'benchexec.tablegenerator': ['template.*']},
    entry_points = {
        "console_scripts": [
            'benchexec = benchexec:main',
            'runexec = benchexec.runexecutor:main',
            'table-generator = benchexec.tablegenerator:main',
            ]
        },
    install_requires = ['tempita==0.5.2'],
    setup_requires=['nose>=1.0'],
    test_suite = 'nose.collector',
    zip_safe = True,
)
