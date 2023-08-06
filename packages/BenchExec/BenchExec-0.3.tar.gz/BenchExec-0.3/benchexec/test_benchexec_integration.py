"""
BenchExec is a framework for reliable benchmarking.
This file is part of BenchExec.

Copyright (C) 2007-2015  Dirk Beyer
All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# prepare for Python 3
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from subprocess import CalledProcessError
sys.dont_write_bytecode = True # prevent creation of .pyc files

here = os.path.dirname(__file__)
base_dir = os.path.join(here, '..')
bin_dir = os.path.join(base_dir, 'bin')
benchexec = os.path.join(bin_dir, 'benchexec')

benchmark_test_file = os.path.join(base_dir, 'doc', 'benchmark-example-rand.xml')
benchmark_test_tasks = ['DTD files', 'Markdown files', 'XML files', 'Dummy tasks']

class BenchExecIntegrationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.longMessage = True
        cls.maxDiff = None

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="BenchExec.benchexec.integration_test")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_cmd(self, *args):
        try:
            output = subprocess.check_output(args=args, stderr=subprocess.STDOUT).decode()
        except CalledProcessError as e:
            print(e.output.decode())
            raise e
        print(output)
        return output

    def run_benchexec_and_compare_expected_files(self, *args, tasks=benchmark_test_tasks, name=None):
        self.run_cmd(*[benchexec, benchmark_test_file,
                       '--outputpath', self.tmp,
                       '--startTime', '2015-01-01 00:00',
                       ] + list(args))
        generated_files = set(os.listdir(self.tmp))

        expected_files = ['logfiles', 'results.txt', 'results.xml'] \
                       + ['results.'+files+'.xml' for files in tasks]
        if name is None:
            basename = 'benchmark-example-rand.2015-01-01_0000.'
        else:
            basename = 'benchmark-example-rand.' + name + '.2015-01-01_0000.'
        expected_files = set(map(lambda x : basename + x, expected_files))
        self.assertSetEqual(generated_files, expected_files, 'Set of generated files differs from set of expected files')
        # TODO find way to compare expected output to generated output

    def test_simple(self):
        self.run_benchexec_and_compare_expected_files()

    def test_simple_select_tasks(self):
        self.run_benchexec_and_compare_expected_files('--tasks', 'DTD files',
                                                      '--tasks', 'XML files',
                                                      tasks=['DTD files', 'XML files'])

    def test_simple_set_name(self):
        test_name = 'integration test'
        self.run_benchexec_and_compare_expected_files('--name', test_name, name=test_name)

    def test_simple_parallel(self):
        self.run_benchexec_and_compare_expected_files('--numOfThreads', '12')
