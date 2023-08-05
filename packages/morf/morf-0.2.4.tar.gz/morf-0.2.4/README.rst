.. Copyright 2013-2014 Oliver Cope
..
.. Licensed under the Apache License, Version 2.0 (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..     http://www.apache.org/licenses/LICENSE-2.0
..
.. Unless required by applicable law or agreed to in writing, software
.. distributed under the License is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.


Morf - web form validation and processing
=========================================

Why use morf?
-------------

Because you want to express simple forms concisely::

    from morf import HTMLForm, fields, validators

    class ContactForm(HTMLForm):
        name = fields.Str(message='Please fill in your name')
        email = fields.Str(validators=[validators.is_email])
        message = fields.Str(validators=[validators.minwords(10)])

Because you want to be able to express custom validation logic::

    class BookingForm(HTMLForm):
        name = fields.Str(message='Please fill in your name')
        arrival_date = fields.Date()
        leaving_date = fields.Date()

        @validates(arrival_date, leaving_date)
        def check_name(self, arrival_date, leaving_date):

            # No minimum booking duration at weekends
            if arrival_date.weekday() in (SAT, SUN):
                return

            if (leaving_date - arrival_date).days < 3:
                self.fail('Sorry, the minimum booking is for 3 days')

Because you want a simple API to work with::

    def my_view(request):
        form = BookingForm(request.POST)
        if form.isvalid:
            make_booking(form.data)
            ...
        else:
            show_error_page(errors=form.errors)


Documentation for morf is available at http://ollycope.com/software/morf/

Morf's source code is available at https://bitbucket.org/ollyc/morf/


Rendering forms with widgets
============================

Morf separates form processing - taking user input and validating it, and
handling any ensuing application logic - from the business of rendering HTML
forms and parsing HTML form encoded data.

If your form is always going to be rendered as an HTML form, just
subclass HTMLForm, and you can use the rendering methods directly::

    class BookingForm(HTMLForm):
        name = fields.Str(message='Please fill in your name')
        email = fields.Str(validators=[is_email])
        arrival_date = fields.Date()
        leaving_date = fields.Date()

    bookingform = BookingForm()
    bookingform.as_p().render()

Forms processing data coming from sources other than HTML form submissions
should subclass ``morf.Form``.

If you also want your form to be rendered or submitted in HTML,
use ``HTMLForm.adapt``::

    from morf import Form, HTMLForm

    class BookingForm(Form):
        name = fields.Str(message='Please fill in your name')
        email = fields.Str(validators=[is_email])
        arrival_date = fields.Date()
        leaving_date = fields.Date()

    HTMLBookingForm = HTMLForm.adapt(BookingForm)
    HTMLBookingForm().as_p().render()

Rendering field groups
-----------------------


Select groups of fields for rendering
using the ``select…`` methods on any
FormRenderer object.

**``select``** returns just the named fields, eg::

    <h1>Personal details</h1>
    {% for field in form.select(['firstname', 'lastname', 'email']) %}
        {{ field.render() }}
    {% endfor %}

    <h1>Address</h1>
    {% for field in form.select(['housenumber', 'street', 'city', 'zip']) %}
        {{ field.render() }}
    {% endfor %}

Note that ``select`` won't raise an exception
if you pass it an invalid field name,
it will just skip that field.
Use ``select([…], strict=True)`` if you want strict fieldname checking.

**``select_except``** returns all the fields except those listed, eg::

    {% for field in form.select_except(['account_type']) %}
        {{ field.render() }}
    {% endfor %}


**``select_to``** returns all the fields up to
(but not including) the named field::

    {% for field in form.select_to(['housenumber']) %}
        {{ field.render() }}
    {% endfor %}

**``select_match``** returns all fields matching a given regular expression::

    <h1>Shipping</h1>
    {% for field in form.select_match(r'shipping_.*') %}
        {{ field.render() }}
    {% endfor %}

    <h1>Billing details</h1>
    {% for field in form.select_match(r'billing_.*') %}
        {{ field.render() }}
    {% endfor %}



HTMLForm
--------

The ``HTMLForm`` class has two important differences over ``Form``.

Firstly,
**HTMLForm has preconfigured rendering options for generating HTML**.
These can be used to render the whole form with fields being wrapped in
``<p>...</p>`` elements, ``<ul>``, ``<ol>`` or as a table::

    form.as_p().render()

    form.as_ul().render()

    form.as_ol().render()

    form.as_table().render()

The ``HTMLForm.renderer`` method lets you customize the rendering templates::

    form.renderer(row_template='<div>{{ field }}</div>')

Secondly,
**HTMLForm adapts nested forms to work with flat HTML forms**.
If you have a form like this, which expects nested data::

    class PlayerForm(HTMLForm):
        last_name = fields.Str()
        first_name = fields.Str()

    class TeamForm(HTMLForm):
        team_name = fields.Str()
        players = fields.ListOf(PlayerForm(), label='Players', spare=2, max=5)

HTMLForm knows how to render this to create HTML inputs like this::

    <input name="team_name" type="text" />
    <input name="players#0.name" type="text" />
    <input name="players#0.age" type="text" />
    <input name="players#1.name" type="text" />
    <input name="players#1.age" type="text" />
    …

And can then convert the corresponding form submission values into the required
data structure, eg::

    {'team_name': 'Surprise!',
     'players': [
        {'name': 'alice',  'age': 8},
        {'name': 'bob', 'age': 7},
        …
    ]}


Widgets
-------

Morf defines various widgets for rendering different HTML field controls.
Specify the widget you want when constructing the field::

    class ContactForm(Form):

        message = field.Str(widget=widgets.Textarea())

If you don't specify a widget, the default widget type for that field will be
used.

Read the source code for ``morf.widgets`` to see the full list of available
widgets.


Fields
======

Morf offers various builtin field types:

- ``morf.fields.Str``
- ``morf.fields.Int``
- ``morf.fields.Decimal``
- ``morf.fields.Date``
- ``morf.fields.DateTime``
- ``morf.fields.Bool``
- ``morf.fields.MultipleChoice``
- ``morf.fields.ListOf``, a container for creating lists of other fields

Additionally, ``morf.form.Form`` can also be used as a field. Typically
you would use this to generate nested structures, eg::


    class PlayerForm(HTMLForm):
        last_name = fields.Str()
        first_name = fields.Str()

    class TeamForm(HTMLForm):
        team_name = fields.Str()
        players = fields.ListOf(PlayerForm(), label='Players', spare=2, max=5)


Field classes take the following standard constructor arguments:

name
    The name of the field (eg 'last_name')

displayname
    The name to display to the user (eg 'last name')
    when referencing the field.
    If not specified this will be generated from ``name``

label
    The label to show for the field
    (eg 'Please enter your last name').
    If not specified ``displayname`` will be used.

empty_message
    The error to display when the field has not been filled in

invalid_message
    The error to display when the field contains invalid data

default
    A default value for the field

processors
    A list of processors. See the `Processors`_ section below

validators
    A list of validators. See the `Validators`_ section below

widget
    The widget to use when rendering as HTML

choices
    A list of choices that the value must be selected from.
    See the `Choices`_ section below.

validate_choices
    If ``choices`` has been set, the submitted value is tested
    to ensure it is a valid item from the list of choices.
    Defaults to ``True``, set this to ``False`` to disable this check.

Choices
-------

Fields can require a value to be selected from a list of valid choices.
Typically this might be represented as radio buttons or a select control.
Choices can be supplied in a variety of ways::

    class UserPreferencesForm(HTMLForm):

        # Choices can be a list of (value, label) tuples
        favorite_color = fields.Str(choices=[('#ff0000', 'Red'),
                                             ('#0000ff', 'Blue')],
                                     widget=widgets.RadioGroup())

        # ...or a list of values doubling as labels
        current_mood = fields.Str(choices=['happy', 'frustrated'],
                                  widget=widgets.RadioGroup())

        # ...or a callable returning either of the two above formats
        shoe_size = fields.Str(choices=range(1, 13),
                            widget=widgets.Select)

        # ...or the name of a method on the form object
        preferred_vegetable = fields.Str(choices='get_vegetables',
                                        widget=widgets.RadioGroup())

        def get_vegetables(self):
            return ['turnip', 'leek', 'potato']


Choices and optgroups
---------------------

Choices can be hierarchical, for example::

    from morf import choices

    soups = [(0, 'Minestrone'), (1, 'French onion')]
    salads = [(2, 'Tomato salad'), (3, 'Greek salad')]]

    class MenuForm(HTMLForm):

        lunch = fields.Choice(choices=[('Soups', choices.OptGroup(soups)),
                                       ('Salads', choices.OptGroup(soups))])

When rendered, the lunch field will be displayed as
an HTML ``<select>`` element containing ``<optgroup>`` elements, eg::

    <select name="lunch">
        <optgroup label="Soups">
            <option value="0">Minestrone</option>
            <option value="1">French onion</option>
        </optgroup>
        <optgroup label="Salads">
            <option value="0">Tomato salad</option>
            <option value="1">Greek salad</option>
        </optgroup>
    </select>


When using radio buttons or checkbox widgets,
``OptGroups`` are rendered inside a ``<fieldset>`` element.

Dynamic fields
--------------

Fields can be added dynamically using ``@property``::

    class FormWithDynamicFields(HTMLForm):

        @property
        def milk_and_sugar(self):
            from datetime import datetime
            beverage = 'coffee' if (datetime.now().hour < 13) else 'tea'
            return fields.Choice(
                    label='How would you like your {}?'.format(beverage),
                    choices=['With milk', 'With sugar', 'With milk and sugar'])

If you need more flexibility use the ``add_fields`` and ``remove_fields``
methods to manipulate the ``fields`` dict.
The ``before`` or ``after`` arguments
allow you to control the ordering of added fields::

    class FormWithDynamicFields(HTMLForm):

        def __init__(self, *args, **kwargs):
            beverage = kwargs.pop('beverage')
            super(FormWithDynamicFields, self).__init__(*args, **kwargs)
            self.add_field('milk_and_sugar',
                            fields.Choice(
                            label='How would you like your {}?'.format(
                                                                  beverage),
                            choices=['with milk',
                                     'with sugar',
                                     'with milk and sugar']),
                            before='biscuit_preference')


Error messages
--------------

Fields can have separate messages specified for empty or invalid data::

    field.Str(empty_message='Choose your new password ',
              invalid_message='Passwords must be at least 8 characters')

You can specify both at once::

    field.Str(message='Choose a new password of at least 8 characters')

Validators can also have error messages::

    field.Str(message='Please enter your length of stay',
              validators=[gt(1, 'You must stay at least one night'),
                          lte(28, 'Rooms cannot be booked for over 28 days')])


Processors
==========

Value processors are run after type conversion but before validation and can
be used for normalizing data input before validation::

    def foldcase(s):
        return s.lower()

    def strip_non_digits(s):
        return re.sub(r'[^\d]', '', s)

    username = field.Str(processors=[foldcase])
    account_no = field.Str(processors=[strip_non_digits])

When writing processors remember that you these should not perform any
validation, so you should never raise ValidationError or any other exception
inside a processor function.


Validators
==========

A validator can be any function or callable object taking the submitted field
value and raising a ValidationError if it fails.

To allow the validation parameters to be varied, the usual pattern is to
define a factory function::

    from morf.validation import assert_true

    def contains(word, message='Invalid value'):
        def validate_contains(value):
            assert_true(word in value.lower(), message)
        return validate_contains


Notice the use of assert_true.
This is exactly equivalent to::

    if word not in value.lower():
        raise ValidationError(message)

You can then use your validator by passing it in the ``validators`` list when
constructing a field::

    field.Str(validators=[contains('please',
                                   message="What's the magic word?")])


Use the ``@validates`` decorator to define a one-off custom validation
condition.
This takes one or more field names,
and each named field is passed as an argument
to the decorated validation function::


        class BookingForm(Form):

            ...

            @validates(arrival_date, leaving_date)
            def check_name(self, arrival_date, leaving_date):

                # No minimum booking duration at weekends
                if arrival_date.weekday() in (SAT, SUN):
                    return

                if (leaving_date - arrival_date).days < 3:
                    self.fail('Sorry, the minimum booking is for 3 days')

You can also use ``@validates`` without arguments,
in which case the validation function is called without arguments
and any errors raised are deemed to apply to the form as a whole::

            @validates
            def validate_entire_form(self, data):
                ...


A variant of ``@validates`` is ``@cleans``,
which replaces the value of the first named field with
the return value of the function::

        class BookingForm(Form):

            ...

            @cleans(card_number)
            def normalize_card_number(self, card_number):

                return card_number\
                    .replace(' ', '')
                    .replace('-', '')
                    .strip()

You can specify multiple field names in the ``@cleans`` decorator,
in which case you must return a tuple of the cleaned values.

Like ``@validates``,
``@cleans`` functions may raise ``ValidationErrors``
(usually by calling ``self.fail``).

You may also use ``@cleans`` without any arguments.
In this case the function will be passed a single argument,
the current value of ``self.data``,
which it may mutate,
or return a new dict of values
to be merged into ``self.data``

Validation running order
------------------------

- Validators bound to field objects are run first.

- Then validation/cleaner functions declared with the
  ``@validates``/``@cleans`` decorators.
  These are run in the order they are declared,
  with the exception that those any form-scope validators
  are pushed to the end
  and only run if all previous validation has passed.

Any ``@validates``/``@cleans`` decorators take optional ``before`` or ``after``
arguments to force a particular run order.


An example::

    class AForm(Form):

        # The minlen validator is the first to be run
        name = fields.Str(validators=[minlen(4)])

        # Validator/cleaner functions are run next
        # in the order they are declared
        @validates(name)
        def validate_name(self, name):
            ...

        @cleans(name)
        def clean_name(self, name):
            return name.strip()

        # This is a form-scoped validator function, which will be run only
        # after all field-scoped validators have been successfully passed
        @validates
        def validate_form(self, data):
            ...

        # This form-scoped validator will be run even if previous validation
        # has failed. Failed fields will not have an entry in the ``data`` dict,
        # so care should be taken not to raise KeyErrors.
        @validates(run_always=True)
        def validate_form2(self, data):
            ...

        # Thie ``before`` argument means this validator will run before
        #  ``validate_form``, even though it was declared later in the file
        @validates(before=validate_form)
        def validate_form3(self, data):
            ...



Binding objects
===============

If you have a form for editing an object
and you want to prepopulate the form
with the existing values
you call ``bind_object``::

    class UserEditForm(Form)

        name = fields.Str()
        email = fields.Str()

    editform = UserEditForm()

    # Binds existing values from `currentuser` to the form fields
    editform.bind_object(currentuser())

You can override the binding of individual fields using keyword arguments.
Suppose that the email address is not an attribute of the user
object, but needs to be accessed from a separate profile object::

    editform.bind_object(currentuser(), email=currentuser().profile.email)


Alternatively you could put this logic in the form class by overriding the
``bind_object`` method::

    class UserEditForm(Form)

        name = fields.Str()
        email = fields.Str()

        def bind_object(self, user, *args, **kwargs):
            super(UserEditForm, self).bind_object(
                    user, email=user.profile.email, *args, **kwargs)


A common pattern is for forms to know how to update model objects, which you
might think of as the inverse of bind_object.

``update_object`` is used for this, for example::

    form = BookingForm(request.POST)
    if form.isvalid:
        booking = Booking()
        form.update_object(booking)
        session.add(booking)


The default implementation of bind_object is very naive, and just copies the
submitted field data over to correspondingly named properties on the model
object. You will probably need to override this.

Binding submitted data
======================

When a user has submits a form, you need to validate it and extract the
processed information. The easiest way is to pass the submitted data in the
constructor::


    form = BookingForm(request.POST)

Any dict like object can be passed here. You can also pass keyword
arguments, which will also be bound to fields::

    form = BookingForm(request.POST, booked_by=currentuser().id)

You can also call ``Form.bind_input`` explicitly::

    form = BookingForm()
    form.bind_input(request.POST)

Calling ``Form.bind_input`` (or passing form data to the constructor)
automatically triggers all validation rules to be run.
Override this by specifying ``validate=False``::

    form = BookingForm()
    form.bind_input(request.POST, validate=False)
