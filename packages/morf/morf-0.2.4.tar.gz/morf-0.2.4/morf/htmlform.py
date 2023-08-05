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

from copy import copy

from .bindadapters import RequestBindAdapter
from .render import RenderOptions, FormRenderer
from .form import Form


class HTMLForm(Form):
    """
    Convenience subclass of form that also implements FormRenderer
    """
    bind_adapter = RequestBindAdapter()
    render_options = RenderOptions()
    render_options.translate_fieldname = bind_adapter.translate_fieldname
    render_with = FormRenderer

    def bind_input(self, raw, *args, **kwargs):
        # Is this an internal recursive call?
        _internal = kwargs.get('_internal', False)
        if not _internal:
            # Split the flat HTML form into nested lists/dicts
            raw = self.bind_adapter(raw)

        return super(HTMLForm, self).bind_input(raw, *args, **kwargs)

    def _bind_input_field(self, field, raw, validate):
        formrenderer = self.render_with(self, self.render_options)
        raw = formrenderer.wrap(field).extract_raw(raw)
        field.bind_input(raw, validate=validate, _internal=True)

    def renderer(self, **kwargs):
        """
        Return a configured FormRenderer instance
        """
        render_options = copy(self.render_options)
        for k, v in kwargs.items():
            setattr(render_options, k, v)
        render_options.convert_templates()
        return self.render_with(self, render_options=render_options)

    def as_p(self, **kwargs):
        return self.renderer(row_template='<p>{{ field }}</p>',
                             **kwargs)

    def as_ul(self, **kwargs):
        return self.renderer(
                form_template='<ul>{{ fields|join() }}</ul>',
                row_template='<li>{{ field }}</li>',
                **kwargs)

    def as_ol(self, **kwargs):
        return self.renderer(
                    form_template='<ol>{{ fields|join() }}</ol>',
                    row_template='<li>{{ field }}</li>',
                    **kwargs)

    def as_table(self, **kwargs):
        return self.renderer(
            form_template='<table><tbody>{{ fields|join() }}</tbody></table>',
            row_template='<tr><td>{{ field }}</td></tr>',
            field_template=('<th>{{ label }}</th>'
                            '<td>{{ errors }}'
                            '<div class="control">{{ control }}</div>'
                            '</td>'),
            **kwargs)

    @classmethod
    def adaptform(cls, formcls):
        class _HTMLForm(cls, formcls):
            pass

        return _HTMLForm
