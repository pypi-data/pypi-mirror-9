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

from .fields import Field


class HTMLFormRenderer(object):

    def __init__(self, form):
        self.form = form

    def render(self, field=None):

        # If field is not specified, render all fields
        if field is None:
            s = ''.join(self.render(f) for f in self.form.fields.values())
            self.fields = []
            return s

        if not isinstance(field, Field):
            field = getattr(self.form, field)

        renderer = self.renderers.get(field) or self.renderers[field.__class__]
        return renderer(field)
