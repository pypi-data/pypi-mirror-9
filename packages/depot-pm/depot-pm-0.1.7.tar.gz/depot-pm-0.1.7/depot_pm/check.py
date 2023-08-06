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
from taskr.contrib.system import os_info, has_command
from taskr.contrib.system.osx import has_app

test_names = [
    'has_command',
]

if os_info.is_osx:
    test_names.append('has_app')


def check(test_name, *args):
    if test_name == 'has_command':
        if not args:
            raise ValueError('At least one argument is required. (command_name)')
        if not has_command(args[0]):
            raise ValueError('No command named "{}".'.format(args[0]))
    elif test_name == 'has_app':
        if not args:
            raise ValueError('At least one argument is required. (app_name)')
        if not has_app(args[0]):
            raise ValueError('No app named "{}".'.format(args[0]))
    else:
        raise ValueError('No such test. ({})'.format(test_name))
