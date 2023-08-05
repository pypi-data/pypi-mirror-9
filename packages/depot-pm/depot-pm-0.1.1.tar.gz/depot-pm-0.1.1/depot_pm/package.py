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


class Package(object):

    def __init__(self, package_source):
        if isinstance(package_source, dict):
            self._name = package_source['package']
            self._test = package_source['test']
        else:
            self._name = package_source
            self._test = None

    @property
    def name(self):
        return self._name

    @property
    def test(self):
        return self._test

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.name)
