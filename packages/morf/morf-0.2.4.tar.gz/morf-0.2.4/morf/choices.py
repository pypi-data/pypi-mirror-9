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

from itertools import chain
from .iterable import iterable


def expand_choices(choices):
    """
    Return an iterator over the available choices.
    The iterator will always yield tuples of ``(value, label)``.
    """
    if callable(choices):
        choices = choices()
    choices = iter(choices)

    try:
        head = next(choices)
        if iterable(head) and len(head) == 2:
            return list(chain([head], choices))
        else:
            return list(chain([(head, head)], ((v, v) for v in choices)))
    except StopIteration:
        return []


class OptGroup(object):
    """
    Mark an optgroup nested in a list of choices
    """
    def __init__(self, choices):
        self.choices = choices

    def __iter__(self):
        return iter(expand_choices(self.choices))
