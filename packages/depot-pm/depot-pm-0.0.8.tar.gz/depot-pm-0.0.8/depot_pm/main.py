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
from collections import OrderedDict
import os
from depot_pm import __version__ as depot_pm_version
from taskr import task, console
from taskr.contrib.system import has_command
import yaml


def resolve_package_content_path(source_path):
    """
    :type source_path: str
    :rtype: str
    """
    dir_path = None
    while not source_path:
        # Go to upper level
        new_dir_path = os.path.split(dir_path)[0] if dir_path else os.getcwd()
        if new_dir_path == dir_path:
            break
        else:
            dir_path = new_dir_path
        # Check file - yaml first
        source_path = os.path.join(dir_path, 'depot.yaml')
        if not os.path.exists(source_path):
            # Check file - json
            source_path = os.path.join(dir_path, 'depot.json')
            if not os.path.exists(source_path):
                source_path = None

    return source_path


default_installers = {
    'pip': {},
    'gem': {},
    'yum': {
        'os': True,
        'sudo': True,
        'syntax': '{} install -y {}',
    },
    'brew': {
        'os': True,
    },
}
"""
keys:
  sudo(bool, default=False),
  os(bool, default=False),
  multiple(bool, default=True),
  syntax(str, default='{} install {}'),
  command(str, default=<installer name>)
"""


@task
@task.set_argument('--package-file', '-p', dest='package_file', help='path of package file')
@task.set_argument('--verbose', '-v', dest='verbose', action='store_true')
@task.set_argument('--dry-run', '-d', dest='dry_run', action='store_true')
def install(package_file=None, verbose=False, dry_run=False):
    # find package content path
    package_content_path = resolve_package_content_path(package_file)
    if package_content_path and os.path.exists(package_content_path):
        if verbose:
            console.info('resolved package file: {}'.format(package_content_path))
    else:
        if verbose:
            console.error('Cannot find package file.')
        task.exit(1)
        return  # suppress pycharm warning

    # parse it
    with open(package_content_path, 'r') as f:
        try:
            package_content = yaml.load(f)
            """:type: dict[str, dict]"""
        except yaml.YAMLError as e:
            if verbose:
                console.error('Cannot parse package file: {}'.format(e))
            task.exit(2)
            return  # suppress pycharm warning
        else:
            installers = None
            """:type: dict[str, dict]"""
            packages = None
            """:type: dict"""
            if package_content:
                # copy default installers
                installers = dict(default_installers)
                installers.update(package_content.get('installers', {}))
                # Get packages
                packages = package_content.get('packages', None)
                # populate/finalize installers
                empty_installers = []
                for installer, installer_config in installers.items():
                    # Get packages of this installer
                    installer_packages = packages.pop(installer, None)
                    if not installer_packages:
                        # No packages for this installer ... pop it
                        empty_installers.append(installer)
                        continue
                    # Create installer_config if it's empty
                    if not installer_config:
                        installer_config = installers[installer] = {}
                    # Setup packages
                    installer_config['packages'] = installer_packages
                # Clean up
                for empty_installer in empty_installers:
                    installers.pop(empty_installer)
                # Sort installers by os-specific or not
                # (OS specific installers should be install first)
                installers = OrderedDict(sorted([(installer_name, installer_config)
                                                 for installer_name, installer_config in installers.items()],
                                                key=lambda installer_set: installer_set[1].get('os', False),
                                                reverse=True))
            # No installer ... pop
            if not installers:
                if verbose:
                    console.warn('Empty package content file')
                task.exit(0)
            # some packages are not consumed by installers ... pop
            if packages:
                if verbose:
                    console.error('Unknown installers: {}. Please setup them in "installers" section'.
                                  format(', '.join(packages.keys())))
                task.exit(1)

    # Go
    if dry_run and verbose:
        console.info('dry run: depot-pm won\'t perfom following commands.')
    for installer, installer_config in installers.items():
        # Get configs
        require_sudo = installer_config.get('sudo', False)
        support_multiple_packages = installer_config.get('multiple', True)
        command_syntax = installer_config.get('syntax', '{} install {}')
        command_name = installer_config.get('command', installer)
        packages = installer_config['packages']

        # Check installer
        if not has_command(command_name):
            if verbose:
                console.warn('Could not found {}. depot-pm will skip it.'.format(command_name))
            continue

        commands = []
        # Make commands
        if support_multiple_packages:
            command = command_syntax.format(command_name, ' '.join(packages))
            if require_sudo:
                command = 'sudo {}'.format(command)
            commands.append(command)
        else:
            for package in packages:
                command = command_syntax.format(command_name, package)
                if require_sudo:
                    command = 'sudo {}'.format(command)
                commands.append(command)

        # Go
        if verbose:
            console.info('Install packages via {}. Packages: [{}]'.format(installer, ', '.join(packages)))
        for command in commands:
            if dry_run:
                console.show(command)
            else:
                os.system(command)

    if verbose:
        console.success('done')


@task
def version():
    print('depot-pm {}'.format(depot_pm_version))


if __name__ == '__main__':
    task.dispatch()
