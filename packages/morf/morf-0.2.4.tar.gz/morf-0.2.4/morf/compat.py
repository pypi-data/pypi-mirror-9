# Copyright 2013-2014 Oliver Cope
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

import sys

PY2 = sys.version_info[0] <= 2

if PY2:
    ustr = unicode
else:
    ustr = str


def implements_to_str(cls):
    if PY2:
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda cls: cls.__unicode__().encode('utf8')
    return cls


def implements_bool(cls):
    if PY2:
        cls.__nonzero__ = cls.__bool__
        del cls.__bool__
    return cls
