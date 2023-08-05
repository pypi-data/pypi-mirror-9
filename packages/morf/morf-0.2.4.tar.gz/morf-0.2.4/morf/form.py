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
from collections import Mapping
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict  # noqa
from inspect import getmembers
from itertools import count

from . import fields
from . import render
from . import exceptions
from .types import Undefined, AttrDict


#: Global registry of registered validation functions
_validators = {}


class ValidatorOpts(object):

    def __init__(self, is_cleaner=False, run_always=False):
        self.is_cleaner = is_cleaner
        self.run_always = run_always


def register_validator(func, fieldnames, _validates_ordering=count(),
                       before=None, after=None, **opts):
    validates = getattr(func, '__validates__', [])
    ordering = next(_validates_ordering)

    if before:
        before = getattr(before, 'im_func', before)
        ordering = _validators[before][0][0]
        for vs in _validators.values():
            for ix, v in enumerate(vs):
                if v[0] >= ordering:
                    vs[ix] = (v[0] + 1,) + v[1:]

    if after:
        after = getattr(after, 'im_func', after)
        ordering = _validators[after][0][0]
        for vs in _validators.values():
            for ix, v in enumerate(vs):
                if v[0] <= ordering:
                    vs[ix] = (v[0] - 1,) + v[1:]

    validates.append((ordering, fieldnames, ValidatorOpts(**opts)))
    _validators[func] = func.__validates__ = validates
    return func


def validates(*fieldnames, **kwargs):
    """
    Register a validator function.

    :param fieldnames: list of fieldnames to validate. If empty, it will be
                       considered a form-scope validator and only run after all
                       other validation has run and passed.
    :param run_always: Applies to form-scope validation only. If ``True`` the
                       validation function will be run even when previous
                       validators have failed.
    :param before: Run this validator before the given function
    """

    def _validates(func, fieldnames=fieldnames):
        register_validator(func, fieldnames, **kwargs)
        return func

    if len(fieldnames) == 1 and callable(fieldnames[0]):
        return _validates(fieldnames[0], tuple())

    return _validates


def cleans(*fieldnames, **kwargs):
    """
    Register a cleaner function.

    :param fieldnames: list of fieldnames to clean. If empty, it will be
                       considered a form-scope validator and only run after all
                       other validation has run and passed.
    :param run_always: Applies to form-scope validation only. If ``True`` the
                       validation function will be run even when previous
                       validators have failed.
    :param before: Run this validator before the given function
    """

    def _cleans(func, fieldnames=fieldnames):
        register_validator(func, fieldnames,
                           is_cleaner=True,
                           **kwargs)
        return func

    if len(fieldnames) == 1 and callable(fieldnames[0]):
        return _cleans(fieldnames[0], tuple())

    return _cleans


def _isfield(f):
    return isinstance(f, fields.FieldBase)


class Form(fields.FieldBase):
    """
    The base class for forms
    """

    render_with = render.FormRenderer
    dimensionality = fields.FieldBase.DICT
    bound_objects = []

    def __init__(self, raw=None, bind=None):

        super(Form, self).__init__()
        self._initfields()

        self.raw = {}
        self.data = self.value = AttrDict()

        if bind:
            self.bind_object(bind)

        if raw is not None:
            self.bind_input(raw)

    def _initfields(self):
        """
        Make independent copies of all fields associated to the form, and
        assign their _parent, fieldname etc attributes
        """
        fs = []
        for name, item in getmembers(self):
            if _isfield(item):
                field = copy(item)
                fs.append((name, field))

        fs.sort(key=lambda a: a[1].ordering)
        for name, f in fs:
            f._parent = self
            if f.fieldname is None:
                f.fieldname = name

        self.fields = OrderedDict(fs)

    def __getstate__(self):
        state = self.__dict__.copy()
        assert state['data'] is state['value']
        # Remove
        del state['value']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.value = self.data
        self._initfields()

    def bind_object(self, ob=None, *args, **kwargs):
        """
        Bind form values to attributes found in ``ob``

        Multiple objects may be specified as additional positional args.
        In this case properties will be looked up on all objects, with values
        from later objects overriding earlier listed ones.

        :param ob: The object to bind to
        :param *args: Additional objects to bind to. Later listed items take
                      precendence over earlier ones
        :param *kwargs: Additional keyword arguments to bind to. Takes
                        precedence over all previous arguments.
        """
        _marker = []
        self.bound_objects = args = (ob,) + args + (kwargs,)

        for name, f in self.fields.items():
            value = _marker
            for ob in reversed(args):
                if isinstance(ob, Mapping):
                    try:
                        value = ob[name]
                        break
                    except KeyError:
                        pass
                else:
                    value = getattr(ob, name, _marker)
                    if value is not _marker:
                        break

            if value is not _marker:
                f.bind_object(value)
                self.raw[name] = f.raw
                self.data[name] = f.value

    def bind_input(self, raw, **kwargs):
        if raw is Undefined:
            raw = {}
        validate = kwargs.pop('validate', True)
        kwargs.pop('_internal', False)
        self.raw = dict(raw, **kwargs)
        self.errors = []
        self.data = self.value = AttrDict()

        for name, f in self.fields.items():
            value = self.raw.get(f.fieldname, Undefined)
            self._bind_input_field(f, value, validate)
            self.errors.extend((name, message) for message in f.errors)
            if f.value is not Undefined:
                self.data[name] = f.value

        if validate:
            self.call_form_validators()

    def _bind_input_field(self, field, raw, validate):
        field.bind_input(raw, validate=validate, _internal=True)

    @property
    def bound_object(self):
        if not self.bound_objects:
            return None
        return self.bound_objects[0]

    def get(self, key, default=None):
        return self.data.get(key, default)

    def __getitem__(self, key):
        return self.data[key]

    def add_field(self, name, field, after=None, before=None):
        """
        Add a field to the form.

        :param name: The fieldname to use
        :param field: A field object
        """
        field._parent = self

        if field.fieldname is None:
            field.fieldname = name

        if after is before is None:
            self.fields[name] = field
        else:
            fields = OrderedDict()
            for n, f in self.fields.items():
                if n == before:
                    fields[name] = field
                    fields[n] = f
                elif n == after:
                    fields[n] = f
                    fields[name] = field
                else:
                    fields[n] = f
            if name not in fields:
                raise KeyError(before or after)
            self.fields = fields

    def remove_field(self, name):
        del self.fields[name]

    def _get_validators(self):
        """
        Return a sorted list of form-level validators and cleaners (declared
        via the @validates, @cleans decorators).

        The list is sorted by:

        - Does it run against named fields?
          (field-scope validators are sorted before form-scope)
        - Then in declaration order
        """
        cls_field_to_name = \
                dict((v, k) for k, v in getmembers(self.__class__, _isfield))
        vs = []
        for __, func in getmembers(self):
            for order, fieldnames, opts in getattr(func, '__validates__', []):
                fieldnames = tuple(cls_field_to_name[f] if _isfield(f) else f
                                   for f in fieldnames)
                if all(f in self.fields for f in fieldnames):
                    sort_key = (not bool(fieldnames), order)
                    vs.append((sort_key, (func, fieldnames, opts)))
                else:
                    badfields = [f for f in fieldnames if f not in self.fields]
                    raise AssertionError(
                        "%r references non-existant fields %r" %
                        (func, badfields))

        vs.sort()
        vs = [item for __, item in vs]
        return vs

    def call_form_validators(self, _marker=[]):

        for func, fieldnames, opts in self._get_validators():
            try:
                values = tuple(self.data[f] for f in fieldnames)
            except KeyError:
                # One or more of the fieldnames has not passed initial
                # validation. Skip this item
                continue

            form_scoped = not bool(values)

            if not opts.run_always:
                # Don't run form-scope validators if other validation has
                # failed
                if form_scoped and self.errors:
                    continue

                else:
                    # Don't run field validators if other validation on that
                    # field has already failed
                    failed_fields = set(f for f, _ in self.errors)
                    if set(fieldnames) & failed_fields:
                        continue

            try:
                if form_scoped:
                    values = (self.data,)
                result = func(*values)
                if opts.is_cleaner:
                    fieldc = len(fieldnames)
                    if fieldc == 0:
                        if result is not None:
                            result = result.items()
                        else:
                            result = []

                    elif fieldc == 1:
                        result = [(fieldnames[0], result)]
                    else:
                        assert (isinstance(result, tuple) and
                                len(result) == fieldc),\
                            "%r validates %d fields but did not return a "\
                            "tuple of length %d" % (result, fieldc, fieldc)
                        result = zip(fieldnames, result)
                    for fieldname, value in result:
                        self.data[fieldname] = value
                        try:
                            self.fields[fieldname].value = value
                        except KeyError:
                            pass
            except exceptions.ValidationError as e:
                try:
                    associated = self.fields[fieldnames[0]]
                except IndexError:
                    associated = None

                message = e.message or \
                            (associated and associated.invalid_message) or \
                            "validator '{0!r}' failed but did not " \
                            "provide a message".format(func)

                fieldname = associated and associated.fieldname or None
                self.errors.append((fieldname, message))
                if fieldname in self.fields:
                    self.fields[fieldname].errors.append(message)

    def add_error(self, field, message):
        if isinstance(field, fields.Field):
            if field.fieldname:
                field = field.fieldname
            else:
                raise ValueError("%r does not have a valid fieldname")

        assert field is None or field in self.fields
        self.errors.append((field, message))

    def validate(self, field, validator, message=None):

        if isinstance(field, fields.Field):
            field = field.fieldname

        try:
            validator(self.data[field])
        except exceptions.ValidationError as e:
            m = message or e.message or self.fields[field].invalid_message
            self.errors.append((field, m))
            return

    def is_considered_empty(self, value):
        if value is None or value is Undefined:
            return True
        for f in self.fields.values():
            try:
                v = value[f.fieldname]
            except KeyError:
                continue
            if not f.is_considered_empty(v):
                return False
        return True

    def create_object(self):
        raise NotImplementedError

    def update_object(self, ob, exclude=frozenset()):
        """
        Update object ``ob`` with attributes from the submitted data.

        :param ob: the object to update
        :param exclude: attributes to skip when updating
        """
        for key, value in self.data.items():
            if key not in exclude:
                setattr(ob, key, value)
