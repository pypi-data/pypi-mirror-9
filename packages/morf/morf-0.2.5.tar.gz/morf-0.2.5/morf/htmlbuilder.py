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

from markupsafe import Markup, escape

from .compat import ustr, implements_to_str

EMPTY_ELEMENTS = set(['area', 'base', 'basefont', 'br', 'col', 'frame', 'hr',
                      'img', 'input', 'isindex', 'link', 'meta', 'param'])


class _TagMeta(type):

    def __getattr__(cls, name):
        return cls.__class__(name, (cls,), {'name': name})

_Tag = _TagMeta('_Tag', (object,), {})


@implements_to_str
class Tag(_Tag):

    name = None

    def __init__(self, *args, **kwattrs):

        self.attrs = {}
        self.children = []
        self.update(*args, **kwattrs)

    def update(self, *args, **kwattrs):
        for item in args:
            if isinstance(item, (Tag, ustr, bytes)):
                self.children.append(item)
            else:
                self.children.extend(item)

        for k, v in kwattrs.items():
            if k[-1] == '_':
                self.attrs[k[:-1]] = v
            else:
                self.attrs[k] = v
        return self

    __call__ = update

    def tohtml(self, dialect='xhtml'):
        return dialects[dialect].format(self)

    def __str__(self):
        return self.tohtml()

    def __html__(self):
        return self.tohtml()


class _HTMLFormatter(object):

    empty = Markup('<{0}{1} />')
    children = Markup('<{0}{1}>{2}</{0}>')
    nochildren = Markup('<{0}{1}></{0}>')
    fragment = Markup('{2}')

    def format_attrs(self, tag):
        return Markup('').join(Markup(' {0}="{1}"').format(k, v)
                               for k, v in sorted(tag.attrs.items())
                               if v is not None)

    def format(self, tag):
        if not isinstance(tag, Tag):
            return escape(tag)

        if tag.name is None:
            formatstr = self.fragment

        elif tag.children:
            formatstr = self.children

        elif tag.name in EMPTY_ELEMENTS:
            formatstr = self.empty

        else:
            formatstr = self.nochildren

        return formatstr.format(tag.name,
                                self.format_attrs(tag),
                                Markup('').join(self.format(c)
                                                for c in tag.children))


class XHTMLFormatter(_HTMLFormatter):
    pass


class HTMLFormatter(_HTMLFormatter):
    empty = Markup('<{0}{1}>')


dialects = {'xhtml': XHTMLFormatter(),
            'html': HTMLFormatter()}
