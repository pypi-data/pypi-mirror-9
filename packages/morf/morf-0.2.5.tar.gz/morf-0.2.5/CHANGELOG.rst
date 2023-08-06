0.2.5
-----

- fields now have a 'hidden' argument in the constructor, eg
  ``myfield = fields.Int(hidden=True)``.
- fields.Int and fields.Decimal are now rendered by a <input type="number">
  control by default.
- Bugfix: calling copy() on a form object copies over all fields, including
  those added at runtime via Form.add_field.

0.2.4
-----

- Widgets now have access to the ``field.value``, not just the string
  representation in ``field.raw``.
- Removed the ``**kwargs`` argument from Form.__init__. If you need to
  call bind_input with keyword arguments you must now do so explicitly
  in a separate call to bind_input.

0.2.3
-----

- The HTML rendering for radio and checkbox widgets has been changed to make
  it possible to target the label of checked inputs in CSS.
- Bugfix: calling ``FormRenderer.visible()`` after ``FormRenderer.pop()``
  no longer causes an error.

0.2.2
-----

- An ``after`` argument was added to the @cleans and @validates decorators
  to force a validation/cleaning function to run after another has already
  completed.
- @cleans and @validates functions are no longer called if associated with
  fields that have failed a previous validation check.
- Added ``Form.add_field`` and ``Form.remove_field`` for manipulating fields
  dynamically

0.2.1
-----

- Bound form fields are now only accessible via the ``Form.fields`` dictionary.
  This removes the need to maintain two synchronized mapppings of form fields.
- Form.bind_object no longer requires a positional argument and can now also
  accept dictionaries as arguments
- Bugfix: Choice fields no longer raise ``ValidationError``\s if ``None`` or
  the empty string are used as choice values


0.2
---

- All ``render_*`` methods now return ``markupsafe.Markup`` objects
- An ``exclude`` argument was added to the default ``Form.update_object``
  implementation, allowing subclasses to more easily override the updating of
  specific attributes, and allowing ``Form.update_object`` to manage the
  remainder.


0.1
---

- Initial release
