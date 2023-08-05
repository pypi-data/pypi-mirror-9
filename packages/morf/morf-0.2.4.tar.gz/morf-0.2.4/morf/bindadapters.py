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

import re
import warnings
from functools import partial


class BindAdapter(object):

    def __call__(self, raw):
        """
        Return the raw input (eg a flat list of key/value pairs from an HTML
        form submission) transformed into the properly nested data structure
        ready to pass on to Form.bind.
        """
        return raw

    def translate_fieldname(self, field):
        """
        Return the (possibly transformed) name to use for the field
        """
        return field.fieldname


class RequestBindAdapter(BindAdapter):
    """
    Adapt a typical request dictionary to an unpacked hierarchy of lists and
    dictionaries.

        >>> data = {
        ...     'person#0.name': 'eric',
        ...     'person#0.job#0': 'ordinary schoolboy',
        ...     'person#0.job#1': 'superhero',
        ...     'person#1.name': 'mr benn',
        ...     'person#1.job#0': 'businessman',
        ...     'person#1.job#1': 'astronaut',
        ...     'person#1.job#2': 'balloonist',
        ... }
        >>> adapt = RequestBindAdapter()
        >>> adapt(data) == {
        ...     'person' : [
        ...         {'name': 'eric',
        ...          'job': ['ordinary schoolboy', 'superhero']},
        ...         {'name': 'mr benn',
        ...          'job': ['businessman', 'astronaut', 'balloonist']}
        ...     ],
        ... }
        True
    """

    mixed_key_message = ("Form submission contains mixed dict and list keys. "
                         "Skipping {0!r}")

    list_separator = '#'
    dict_separator = '.'
    unnumbered_list_separator = '[]'

    def __init__(self):
        unnumbered_list_pattern = \
                '{0}(?P<U>)'.format(re.escape(self.unnumbered_list_separator))
        numbered_list_pattern = \
                '{0}(?P<N>\d+)'.format(re.escape(self.list_separator))
        dict_pattern = \
                '{0}(?P<D>([^\.#\[]+))'.format(re.escape(self.dict_separator))
        self._finder = re.compile('|'.join([numbered_list_pattern,
                                            unnumbered_list_pattern,
                                            dict_pattern])).finditer

    def warn_mixed_key(self, path):
        warnings.warn(self.mixed_key_message.format(path), stacklevel=400)

    def __call__(self, raw):
        data = {}
        list_surrogates = {}

        for path, value in iterallitems(raw):
            curdata = data
            curkey = None
            # setval is initally a no-op
            setval = lambda k: data
            for match in self._finder('.' + path):
                identity = (id(curdata), curkey)
                match = match.groupdict()
                # Dictionary
                if match['D'] is not None:
                    if identity in list_surrogates:
                        self.warn_mixed_key(path)
                        continue
                    curdata = setval({})
                    curkey = match['D']
                    setval = partial(curdata.setdefault, curkey)

                # Numbered list
                elif match['N'] is not None:
                    l = setval({})
                    if l and identity not in list_surrogates:
                        self.warn_mixed_key(path)
                        continue
                    list_surrogates[(id(curdata), curkey)] = \
                                            (curdata, curkey, l)
                    curdata = l
                    curkey = match['N']
                    setval = partial(curdata.setdefault, curkey)

                # Unnumbered list
                elif match['U'] is not None:
                    l = setval({})
                    if l and identity not in list_surrogates:
                        self.warn_mixed_key(path)
                        continue
                    list_surrogates[(id(curdata), curkey)] = \
                                            (curdata, curkey, l)
                    curdata = l
                    curkey = len(curdata)
                    setval = partial(curdata.setdefault, curkey)

            setval(value)

        for parent, key, l in list_surrogates.values():
            parent[key] = [l[k] for k in sorted(l)]

        return data

    def translate_fieldname(self, field):
        names = []
        while True:
            parent = field._parent
            name = field.fieldname
            if field.dimensionality == field.SIMPLE_LIST:
                name = name + self.unnumbered_list_separator
            names.append(name)

            if parent and parent.fieldname:
                if parent.dimensionality == field.DICT:
                    names.append(self.dict_separator)
                elif parent.dimensionality == field.LIST:
                    names.append(self.list_separator)
                else:
                    raise Exception("Can't handle field {0!r}".format(parent))
                field = parent
            else:
                break

        return ''.join(reversed(names))


def iterallitems(raw):
    """
    Try all common patterns for iterating over all multidict pairs from
    ``raw``.

    Aims for compatibility with Flask, Fresco, WebOb and Django request objects
    """
    # Fresco
    try:
        return raw.allitems()
    except AttributeError:
        pass

    # Werkzeug
    try:
        return raw.iteritems(multi=True)
    except (AttributeError, TypeError):
        pass

    # Django
    try:
        def items(items=raw.iterlists()):
            for k, vs in items:
                for v in vs:
                    yield k, v
        return items()
    except AttributeError:
        pass

    # WebOb, regular dict
    try:
        return raw.iteritems()
    except AttributeError:
        pass

    # Python 3 dicts (no iteritems method)
    try:
        return raw.items()
    except AttributeError:
        pass

    # Fallback - assume is already an iterator or list
    return iter(raw)
