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

from collections import MutableSequence, MutableSet, MutableMapping
from copy import copy
from datetime import datetime
from itertools import count
import decimal

import dateutil.parser

from . import widgets, render, validators as morf_validators
from .exceptions import ValidationError
from .types import Undefined, AttrDict
from .compat import ustr
from .choices import expand_choices, OptGroup
from .iterable import iterable

_marker = []
_ordering = count()


VALUE_EXPECTED = 'This field is required'
INVALID = 'Invalid value'


def coalesce(*args, **kwargs):
    null = kwargs.pop('null', None)
    try:
        return next(a for a in args if a is not null)
    except StopIteration:
        return None


def make_displayname(s):
    """
    Convert a field name to an appropriate label, eg
    from ``'a_field'`` to ``'A field'``
    """
    if s is None:
        return
    return s.replace('_', ' ').capitalize()


class FieldBase(object):
    """
    The base field class.

    As well as regular fields (see :class:`Field`),
    this is also the base for :class:`morf.form.Form`
    """

    #: A field representing a single dimensioned value, eg a string or number
    SCALAR = 'scalar'

    #: A field representing a mapping of multiple values, eg an entire form
    DICT = 'scalar'

    #: A field representing an ordered set of values, each of which may be of
    #: any type
    LIST = 'list'

    #: A field representing an ordered set of values, each of which must be a
    #: scalar type
    SIMPLE_LIST = 'simplelist'

    default = Undefined
    empty_values = set()

    _fieldname = None
    _initial = None

    #: The display name for the field.
    #: Example: 'email address'
    displayname = None

    #: The label to display next to the field.
    #: Example: 'Please enter your email address'
    label = None

    #: Valid choices, typically used for a select or radio group field
    choices = None

    #: The default class to use to render the field (label, errors, control)
    render_with = render.FieldRenderer

    #: The widget to use to render just the field's control
    widget = widgets.TextInput

    #: Does the field encode a single scalar value, a mapping or a list?
    #: Used by RequestBindAdapter to generate appropriate fieldnames
    dimensionality = SCALAR

    #: A reference to the parent form or field if the field is in a list
    #: or subform
    _parent = None

    def __init__(self):
        self.ordering = next(_ordering)
        self.raw = Undefined
        self.value = Undefined
        self.errors = []

    @property
    def is_valid(self):
        return not bool(self.errors)

    def fail(self, message=None):
        raise ValidationError(message)

    def __getstate__(self):
        """
        Return the object's state for copying.

        All mutable top-level attributes (eg processors and validators) are
        independently copied.
        """
        mutable_types = (MutableSequence, MutableSet, MutableMapping)
        return dict((k, copy(v) if isinstance(v, mutable_types) else v)
                    for k, v in self.__dict__.items())

    def extract_raw(self, raw):
        """
        Process the raw value given to us by the form.
        For compound fields this could be a list or dict
        (eg a date separated into ``{'d': ..., 'm': ..., 'y': ...}``
        components) which need to be processed into a single value.
        """
        return raw

    def bind_input(self, raw, validate=True, _internal=False):
        """
        Bind the raw submitted value to the field

        Field.extract_raw can be used to extract the raw value in the correct
        format for this method.
        """
        self.raw = raw
        self.value = Undefined
        if not validate:
            return self

        if self.is_considered_empty(self.raw):
            if self.default is not Undefined:
                self.value = self.default
            else:
                self.errors.append(self.empty_message)
        else:
            try:
                value = self.convert(self.raw)
            except ValidationError as e:
                self.errors.append(e.message or self.invalid_message)
                return self
            value = self.process_value(value)
            self.validate(value)
            self.value = value

        return self

    def bind_object(self, ob):
        self.raw = self.rconvert(ob)
        self.value = ob

    def process(self, value):
        """
        A convenience method for binding a raw value and returning the
        processed value (or raising a ValidationError)
        """
        field = copy(self)
        field.bind_input(value)
        if field.errors:
            raise ValidationError(field.errors[0])
        return field.value

    def convert(self, input_value):
        """
        Return ``input_value`` converted to the required type, or raise a
        ValidationError
        """
        return input_value

    def rconvert(self, ob):
        """
        Reverse convert ``ob`` to a raw input value
        """
        if ob is None:
            return None
        return ustr(ob)

    def process_value(self, value):
        """
        Apply any processing to ``value`` and return the new value.

        Processing might include operations such as trimming whitespace from
        strings, and happens after type conversion but before validation.
        """
        return value

    def validate(self, value):
        """
        Apply any required validation rules to ``value`` and raise
        ``ValidationError`` if any condition is not met.
        """

    def is_considered_empty(self, value):
        """
        Return true if the given value is considered empty, triggering
        the field's default value to be used instead.
        """
        try:
            return value is Undefined or value in self.empty_values
        except TypeError:
            # Raised if value is not hashable
            return False

    def _get_fieldname(self):
        """
        The name of the field. Used as the html name attribute when rendering
        form controls. Example: ``'email'``
        """
        return self._fieldname

    def _set_fieldname(self, name):
        self._fieldname = name
        self.displayname = coalesce(self.displayname, self.label,
                                    make_displayname(name))
        self.label = coalesce(self.label, self.displayname)

    fieldname = property(_get_fieldname, _set_fieldname)

    def _get_initial(self):
        return self._initial

    def _set_initial(self, v):
        self._initial = v
        if self.raw is Undefined:
            self.bind_object(v)

    initial = property(_get_initial, _set_initial)


class Field(FieldBase):
    """
    Base class for all field types (except :class:`morf.form.Form`, which is a
    special case).
    """

    empty_message = VALUE_EXPECTED
    invalid_message = INVALID
    validators = None
    processors = None
    widget = widgets.TextInput()
    empty_values = set([None, ''])

    def __init__(self, name=None, displayname=None, label=None,
                 empty_message=None, invalid_message=None,
                 message=None, empty_values=None, default=_marker,
                 initial=_marker, processors=None, validators=None,
                 widget=None, choices=None, maxlen=None,
                 **kwargs):

        super(Field, self).__init__()
        self.displayname = displayname
        self.label = label
        self._set_fieldname(name)
        self._choices = choices
        self.empty_message = coalesce(empty_message, message,
                                      self.empty_message)
        self.invalid_message = coalesce(invalid_message, message,
                                        self.invalid_message)
        self.empty_values = coalesce(empty_values, self.empty_values)
        self.processors = coalesce(processors, [])
        self.validators = coalesce(validators, [])
        self.default = coalesce(default, self.default, null=_marker)
        if initial is not _marker:
            self.initial = initial
        self.widget = coalesce(widget, self.widget)
        self.options = AttrDict(kwargs)

        # Shortcut for maxlen as this is such a common validation requirement
        if maxlen is not None:
            self.validators.append(morf_validators.maxlen(maxlen))

        if isinstance(self.widget, type):
            self.widget = self.widget()

    def process_value(self, value):
        for item in self.processors:
            value = item(value)
        return value

    def validate(self, value):
        for v in self.validators:
            try:
                v(value)
            except ValidationError as e:
                self.errors.append(e.message or self.invalid_message)
                return

    def get_choices(self):
        if self._choices is None:
            return None
        if isinstance(self._choices, (ustr, str)):
            parent = self._parent
            while parent:
                try:
                    choices = getattr(parent, self._choices)
                except AttributeError:
                    parent = getattr(parent, '_parent', None)
                    continue
                else:
                    return expand_choices(choices)
            raise AttributeError('%r has no attribute %r' % (self._parent,
                                                             self._choices))
        else:
            return expand_choices(self._choices)

    def set_choices(self, choices):
        self._choices = choices

    choices = property(get_choices, set_choices)

    def choice_values(self, _choices=None):
        """
        Return a flattened list of all values present in the choices property
        """
        if _choices is None:
            _choices = self.choices
        values = []
        for v, l in _choices:
            if isinstance(l, OptGroup):
                values.extend(self.choice_values(l))
            else:
                values.append(v)
        return values


class Int(Field):
    """
    A field for integer value input
    """

    invalid_message = 'Enter a whole number'

    def convert(self, s):
        try:
            return int(s)
        except (TypeError, ValueError):
            raise ValidationError(self.invalid_message)


class Decimal(Field):
    """
    A field for decimal number input
    """

    invalid_message = 'Enter a number'

    def convert(self, s):
        try:
            return decimal.Decimal(s)
        except (ValueError, TypeError, decimal.InvalidOperation):
            raise ValidationError(self.invalid_message)


class DateTime(Field):
    """
    Datetime input field
    """

    invalid_message = 'Enter a date'

    #: Default format for displaying the date
    format = '%Y-%m-%d %H:%M:%S'

    def __init__(self, *args, **kwargs):
        self.format = kwargs.pop('format', self.format)
        super(DateTime, self).__init__(*args, **kwargs)

    def convert(self, s):
        try:
            return datetime.strptime(s, self.format)
        except (TypeError, ValueError):
            pass
        try:
            return dateutil.parser.parse(s, **self.options)
        except (TypeError, ValueError):
            raise ValidationError(self.invalid_message)

    def rconvert(self, ob):
        if ob is None:
            return ob
        return ob.strftime(self.format)


class Time(DateTime):
    """
    Time input field
    """

    invalid_message = 'Enter a time'

    #: Default format for displaying the time
    format = '%H:%M:%S'

    def convert(self, s):
        return super(Time, self).convert(s).time()


class Date(DateTime):
    """
    Date input field
    """

    invalid_message = 'Enter a date'
    format = '%Y-%m-%d'

    def convert(self, s):
        return super(Date, self).convert(s).date()


class Str(Field):
    """
    String field
    """

    def convert(self, s):
        return ustr(s)


class Bool(Field):

    widget = widgets.Checkbox

    def __init__(self, *args, **kwargs):
        self.falsevalues = kwargs.pop('falsevalues', None)
        kwargs.setdefault('default', False)
        super(Bool, self).__init__(*args, **kwargs)

    def is_considered_empty(self, value):
        return False

    def convert(self, s):
        if self.falsevalues:
            return s not in self.falsevalues
        else:
            return bool(s)

    def rconvert(self, ob):
        return bool(ob)

    def validate(self, value):
        super(Bool, self).validate(value)


class Constant(Field):

    render_with = render.NullRenderer

    def __init__(self, value, *args, **kwargs):
        super(Constant, self).__init__()
        self.value = value

    def bind_input(self, raw, validate=True, _internal=False):
        return super(Constant, self).bind_input(self.value, validate=validate,
                                                _internal=False)

    def bind_object(self, raw):
        return super(Constant, self).bind_object(self.value)

    def is_considered_empty(self, value):
        return False


class Object(Field):
    """
    A field type that attempts no type conversion of the value passed,
    treating it as an opaque object.
    """

    def convert(self, s):
        return s

    def rconvert(self, s):
        return s


class Hidden(Field):
    """
    A hidden field
    """

    render_with = render.HiddenRenderer
    widget = widgets.HiddenInput


class ListOf(Field):
    """
    A field holding a list of other fields
    """

    render_with = render.ListRenderer
    dimensionality = Field.LIST

    def __init__(self, field, *args, **kwargs):
        """
        :param spare: When rendered, specified how many 'spare' items to render
        :param trim_empty: If true, any items that are not populated will be
                           deleted from the list when binding
        :param: min: The minimum number of fields to display.
                     This takes precendence over ``spare``: the minimum number
                     will always be shown, even if spare is set to zero.
        :param: max: The maximum number of fields to display.
                     This takes precendence over ``spare``: once the maximum
                     number of fields is reached, no spare fields will be
                     added.

        """
        self.spare = kwargs.pop('spare', 1)
        self.trim_empty = kwargs.pop('trim_empty', True)
        self.min = kwargs.pop('min', None)
        self.max = kwargs.pop('max', None)
        self.template_field = field
        self.counter = count()
        self.value = []
        self.fields = []
        self.allerrors = []
        super(ListOf, self).__init__(*args, **kwargs)

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.counter = count()

    def bind_input(self, raw, validate=True, _internal=False):
        if raw is Undefined:
            raw = []
        self.raw = raw
        self.value = []
        self.errors = []
        self.allerrors = []
        if not iterable(raw):
            raw = [raw]
        for item in raw:
            if self.trim_empty and \
                    self.template_field.is_considered_empty(item):
                continue
            field = self.empty_field()
            field.bind_input(item, validate=validate, _internal=True)
            self.fields.append(field)
            self.value.append(field.value)

        if validate:
            self._update_errors()

        return self

    def bind_object(self, ob):
        self.fields = [self.empty_field() for item in ob]
        for field, item in zip(self.fields, ob):
            field.bind_object(item)
        self.value = [f.value for f in self.fields]

    def _update_errors(self):
        self.allerrors = [f.errors for f in self.fields]
        if self.is_valid:
            self.errors = []
        else:
            self.errors = self.allerrors

    def empty_field(self):
        f = copy(self.template_field)
        f.fieldname = ustr(next(self.counter))
        f._parent = self
        return f

    def is_considered_empty(self, value):
        """
        Lists might conceivably be populated by a list or an iterable.
        Calling 'if [] in self.empty_values' gives us an error ([] isn't
        hashable), so to retain flexibility we just check bool(value), which
        will catch empty lists, tuples, Undefined and None.
        """
        return not bool(value)

    @property
    def is_valid(self):
        return not any(self.allerrors)


class Choice(Field):
    """
    A field representing a single choice from a fixed list
    """
    invalid_message = "Select a valid choice"
    widget = widgets.Select()

    def __init__(self, *args, **kwargs):
        self.validate_choices = kwargs.pop('validate_choices', True)
        super(Choice, self).__init__(*args, **kwargs)
        if self._choices is None:
            raise AssertionError("%r must be initialized with a "
                                 "choices argument" % (self,))

    def rconvert(self, value):
        return value

    def validate(self, value):
        if self.validate_choices and value not in set(self.choice_values()):
            self.errors.append(self.invalid_message)
        return super(Choice, self).validate(value)

    def is_considered_empty(self, value):
        return value is Undefined


class MultipleChoice(Choice):
    """
    A field representing a set of choices from a fixed list
    """
    dimensionality = Field.SIMPLE_LIST
    invalid_message = "Select a valid choice"
    widget = widgets.CheckboxGroup()

    def __init__(self, *args, **kwargs):
        super(MultipleChoice, self).__init__(*args, **kwargs)
        if self._choices is None:
            raise AssertionError("MultipleChoice must be initialized with a "
                                 "choices argument")

    def bind_input(self, raw, validate=True, _internal=False):
        if raw is Undefined:
            raw = []
        if not iterable(raw):
            raw = [raw]

        return super(MultipleChoice, self).bind_input(raw, validate, _internal)

    def validate(self, value):
        choice_values = set(self.choice_values())
        if self.validate_choices:
            for item in value:
                if item not in choice_values:
                    self.errors.append(self.invalid_message)

    def bind_object(self, ob):
        self.value = ob
        self.raw = ob
        return self
