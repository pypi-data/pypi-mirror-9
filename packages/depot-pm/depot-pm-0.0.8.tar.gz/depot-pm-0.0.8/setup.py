#!/usr/bin/env python

#
# Copyright 2015 sodastsai
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import unicode_literals, division, absolute_import, print_function
import os
from setuptools import setup, find_packages

from depot_pm import __version__

with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as f:
    long_description = f.read()

setup(name='depot-pm',
      version=__version__,
      url='https://github.com/sodastsai/depot-pm',
      license='Apache License 2.0',
      author='sodas',
      author_email='sodas2002@gmail.com',
      description='depot package manager helps you manage pacakges',
      long_description=long_description,

      packages=find_packages(),
      install_requires=[
          'PyYAML>=3.08',
          'taskr>=0.2.6',
      ],

      entry_points={
          'console_scripts': [
              'depot-pm = depot_pm.main:task.dispatch',
          ],
      },

      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX :: Linux',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Software Development',
          'Topic :: Utilities',
      ])
