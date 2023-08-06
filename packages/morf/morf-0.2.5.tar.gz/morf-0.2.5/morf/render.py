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
from inspect import getmembers
from itertools import takewhile
from weakref import WeakKeyDictionary
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict  # noqa
import re

from jinja2 import Environment, Template
from markupsafe import Markup

from .compat import implements_to_str
from .iterable import iterable

_marker = []
_popped = []

markupjoin = Markup('').join


class RenderOptions(object):
    """
    Set of commonly tweaked parameters for rendering forms and fields
    """
    dialect = 'xhtml'

    jinja2_environ = Environment()
    form_template = '{{ fields|join() }}'
    row_template = '<p>{{ field }}</p>'
    field_template = ('{{ errors }}{{ label }}'
                      '<div class="control">{{ control }}</div>')
    errors_template = (
        '<ul class="errors">'
        '{% for error in errors %}<li>{{ error|e }}</li>{% endfor %}'
        '</ul>')

    label_template = '<label for="{{ id }}">{{ label|e }}</label>'

    def __init__(self, form=None, **kwargs):
        if form:
            self.bind_adapter = form.bind_adapter
        self.__dict__.update(kwargs)
        self.convert_templates()

    def convert_templates(self):
        for name, s in getmembers(self):
            if name.endswith('_template') and not isinstance(s, Template):
                setattr(self, name, self.jinja2_environ.from_string(s))

    def translate_fieldname(self, field):
        return field.fieldname


@implements_to_str
class Renderer(object):
    """
    Renders something, eg a widget, a field or an entire form.
    """
    is_visible = True

    def __init__(self, field, render_options, parent=None):
        """
        :param field: The field object being rendered
        :param render_options: A :class:`~morf.render.RenderOptions` object
        """
        self._field = field
        self._parent = parent
        self.render_options = render_options

    def __call__(self, *args, **kwargs):
        ob = self.copy()
        ob.__init__(*args, **kwargs)
        return ob

    def __str__(self):
        return self.render()

    def __html__(self):
        return self.render()

    def extract_raw(self, raw):
        """
        Extract the raw value for the field from the submitted input values.

        This method is in the Renderer, because it is possible for a field to
        be rendered using a widget that splits the value into multiple inputs
        (eg a time represented as separate 'hh' and 'mm' inputs)
        """
        return raw

    def copy(self):
        """
        Return a copy of the Renderer object.

        All top-level attributes (including mutable structures such as
        processors and validators) are independently copied.
        """
        ob = object.__new__(self.__class__)
        ob.__dict__.update((k, copy(v)) for k, v in self.__dict__.items())
        return ob

    def render(self, **kwargs):
        raise NotImplementedError()


class FieldRenderer(Renderer):

    _id_numbers = WeakKeyDictionary()

    def __init__(self, field, render_options, parent=None):
        super(FieldRenderer, self).__init__(field, render_options, parent)
        self.fieldname = render_options.translate_fieldname(field)
        self._widget = self._field.widget.copy()
        self._widget.configure(fieldname=self.fieldname,
                               raw=field.raw,
                               value=field.value,
                               choices=self._field.choices)

    def extract_raw(self, raw):
        # Delegate to give the widget the chance to extract compound values
        return self._widget.extract_raw(raw)

    @property
    def is_visible(self):
        return self._widget.is_visible

    def render_control(self, **kwargs):
        return self._widget\
                        .render(id=self.get_id(), **kwargs)\
                        .tohtml(self.render_options.dialect)

    def render_label(self):
        return Markup(self.render_options.label_template
                                  .render(id=self.get_id(),
                                          label=self._field.label,
                                          field=self._field))

    def render_errors(self):
        if self._field.is_valid:
            return Markup('')

        return Markup(self.render_options.errors_template.render(
                                errors=self._field.errors, field=self._field))

    def render(self, **kwargs):
        return Markup(self.render_options.field_template.render(
                            control=self.render_control(**kwargs),
                            label=self.render_label(),
                            errors=self.render_errors(),
                            field=self._field,
                            renderer=self))

    def get_id(self):
        """
        Return a unique id, used as the basis for HTML id attributes.

        The id number is incremented with each call. This is so that
        if the field is part of a list widget then each iteration will
        produce a unique id.

        The id number must be a stable series. If the user wishes to script the
        form using javascript, having stable html ids is essential.
        """
        p = self
        while p._parent:
            p = p._parent
        field_counter = self._id_numbers.setdefault(p, {})
        fc = field_counter.setdefault(self._field.fieldname, {})

        count = fc.setdefault(self._field, len(fc))
        return 'field_{0}-{1}'.format(self._field.fieldname, count)

    def __getattr__(self, attr):
        try:
            return self._field.fields[attr]
        except (TypeError, KeyError, AttributeError):
            return getattr(self._field, attr)


class CompoundRendererMixin(object):

    def wrap(self, ob):
        """
        Return ``ob`` wrapped by the appropriate Renderer.
        If no Renderer is available, return ``ob`` unchanged.
        """
        if isinstance(ob, Renderer):
            return ob
        render_with = getattr(ob, 'render_with', None)
        if render_with is not None:
            return render_with(ob, self.render_options, parent=self)
        return ob


class FormRenderer(Renderer, CompoundRendererMixin):

    _fork_origin = None

    def __init__(self, *args, **kwargs):
        super(FormRenderer, self).__init__(*args, **kwargs)
        self._to_render = self._field.fields.copy()

    def __iter__(self):
        return (field for _, field in self._items())

    def __getitem__(self, name):
        """
        Return the named field, wrapped in an appropriate renderer
        """
        return self.wrap(self._field.fields[name])

    def __getattr__(self, attr):
        """
        Proxy attribute access to the underlying Field object
        """
        try:
            return self.wrap(self._field.fields[attr])
        except KeyError:
            return self.wrap(getattr(self._field, attr))

    def _items(self):
        return ((name, self.wrap(field))
                for name, field in self._to_render.items()
                if field is not _popped)

    def _fork(self, fields):
        """
        Return a new copy of the renderer, replacing the ``_to_render``
        dictionary with the named list of fields
        """
        fields = OrderedDict((n, self._to_render[n]) for n in fields)
        # If we have nested calls to _fork
        # (eg form.visible().select(...)) we stuff all the unselected fields
        # back into the fork origin. This makes it possible to do things like:
        #
        # {% for field in form.visible().select(important_fields) %}
        #   <p>{{ field.render() }}</p>
        # {% endfor %}
        #
        # {% for field in form.visible() %}
        #   <p>{{ field.render() }}</p>
        # {% endfor %}
        #
        # And the second loop will skip the fields already rendered.
        for n in fields:
            self._to_render[n] = _popped

        ob = self.__class__.__new__(self.__class__)
        ob.__dict__ = self.__dict__.copy()
        ob._to_render = fields
        ob._fork_origin = self._fork_origin or self

        if self._fork_origin:
            for k, v in self._to_render.items():
                if v is not _popped:
                    self._fork_origin._to_render[k] = v
        return ob

    def pop(self, fieldname, default=_marker):
        field = self._to_render.get(fieldname, _marker)
        if field is _marker or field is _popped:
            if default is _marker:
                raise KeyError(fieldname)
            else:
                return default

        self._to_render[fieldname] = _popped
        return field.render_with(field, self.render_options, parent=self)

    def visible(self):
        """
        Return a FormRenderer with just the visible fields
        """
        return self._fork(name for name, field in self._items()
                          if field.is_visible)

    def hidden(self):
        """
        Return a FormRenderer with just the hidden fields
        """
        return self._fork(name for name, field in self._items()
                          if not field.is_visible)

    def select(self, fields, strict=False):
        """
        Return an iterator over just the named fields.

        The fields will be removed from the internal of fields to
        render so that subsequent iteration over the FormRenderer object
        will not return them a second time.
        """
        if strict:
            for item in fields:
                if item not in self._to_render:
                    raise KeyError(item)
        else:
            _m = object()
            items = ((f, self._to_render.get(f, _m)) for f in fields)
            items = (f for f, v in items if v is not _m)
            return self._fork(items)

    def select_to(self, field):
        """
        Select all fields up to (but not including) the named field.
        See :meth:`select` for more information.
        """
        items = takewhile(lambda n: n != field, self._to_render)
        return self._fork(items)

    def select_match(self, match):
        """
        Select all fields matching the regular expression ``match``.
        The regular expression ``search`` method is used, so match will
        match any part of the fieldname by default, eg:
        ``select_match('address')`` would match both ``address_1`` and
        ``billing_address1``.

        See :meth:`select` for more information.
        """
        if not callable(match):
            match = re.compile(match).search
        items = (f for f in self._to_render if match(f))
        return self._fork(items)

    def select_except(self, fields):
        """
        Select all fields excluding those named.
        See :meth:`select` for more information.
        """
        fields = set(fields)
        items = (f for f in self._to_render if f not in fields)
        return self._fork(items)

    def render(self):
        fields = (self.render_row(f) for f in self)
        return Markup(self.render_options.form_template.render(fields=fields))

    def render_row(self, field):
        return Markup(self.render_options.row_template.render(field=field))


class ListRenderer(FieldRenderer, CompoundRendererMixin):

    def __iter__(self):
        rendered = 0
        for item in self._field.fields:
            yield self.wrap(item)
            rendered += 1

        spare = self._field.spare
        if self._field.min is not None:
            spare = max(self._field.min - rendered, spare)
        if self._field.max is not None:
            spare = min(self._field.max - rendered, spare)

        for ix in range(spare):
            yield self.empty_field()

    @property
    def is_visible(self):
        return self.empty_field().is_visible

    def extract_raw(self, raw):
        items = super(ListRenderer, self).extract_raw(raw)
        if not iterable(items):
            return []
        field = self.empty_field()
        fr = self.wrap(field)

        return [fr.extract_raw(item) for item in items]

    def empty_field(self):
        return self.wrap(self._field.empty_field())

    def render_empty(self, **kwargs):
        return Markup(self.empty_field().render(**kwargs))

    def render_control(self, **kwargs):
        fields = (self.render_row(f, **kwargs) for f in self)
        return Markup(self.render_options.form_template.render(fields=fields))

    def render_row(self, field, **kwargs):
        return Markup(self.render_options.row_template
                .render(field=field.render(**kwargs)))


class NullRenderer(FieldRenderer):
    """
    Produces no output when rendered. Used by :class:`~morf.fields.Constant`
    """
    is_visible = False

    def render_control(self, **kwargs):
        return Markup('')

    def render_label(self):
        return Markup('')

    def render_errors(self):
        return Markup('')

    def render(self, **kwargs):
        return Markup('')


class HiddenRenderer(FieldRenderer):
    """
    Renders an <input type="hidden"> element with no other output. Used by
    :class:`~morf.fields.Hidden`
    """
    is_visible = False

    def render_label(self):
        return Markup('')

    def render_errors(self):
        return Markup('')

    def render(self, **kwargs):
        return self.render_control(**kwargs)
