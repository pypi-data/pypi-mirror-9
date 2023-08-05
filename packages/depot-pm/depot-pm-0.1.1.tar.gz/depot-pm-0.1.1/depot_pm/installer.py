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
from taskr.contrib.system import has_command


class Installer(object):

    def __init__(self, installer_name, **kwargs):
        """
        :type installer_name: str
        """
        self.sudo = kwargs.get('sudo', False)
        """:type: bool"""
        self.os = kwargs.get('os', False)
        """:type: bool"""
        self.multiple = kwargs.get('multiple', True)
        """:type: bool"""
        self.syntax = kwargs.get('syntax', '{} install {}')
        """:type: str"""
        self.command = kwargs.get('command', installer_name)
        """:type: str"""
        self.name = installer_name
        """:type: str"""
        self.packages = kwargs.get('packages', [])
        """:type: list[depot_pm.package.Package]"""

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.name)

    def __iter__(self):
        """
        :rtype: depot_pm.package.Package
        """
        for package in self.packages:
            yield package

    @property
    def available(self):
        return has_command(self.command) and self.packages


default_installers = (
    Installer('pip'),
    Installer('pip3'),
    Installer('gem'),
    Installer('brew', os=True),
    Installer('yum', os=True, sudo=True, syntax='{} install -y {}'),
)
