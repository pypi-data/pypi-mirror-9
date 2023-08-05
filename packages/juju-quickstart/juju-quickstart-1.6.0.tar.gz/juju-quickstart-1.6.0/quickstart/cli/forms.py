# This file is part of the Juju Quickstart Plugin, which lets users set up a
# Juju environment in very few steps (https://launchpad.net/juju-quickstart).
# Copyright (C) 2014 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License version 3, as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Juju Quickstart CLI forms management.

This module contains a collection of functions which help creating and
manipulating forms in Urwid.
"""

from __future__ import unicode_literals

import functools

import urwid

from quickstart.cli import ui


# Define the value used in boolean widgets to specify they allow mixed state.
MIXED = 'mixed'


def _generate(generate_callable, edit_widget):
    """Update the widget contents using the given generate_callable.

    The passed callable function takes no arguments and returns a string.
    """
    edit_widget.set_edit_text(generate_callable())


def _create_generate_widget(generate_callable, edit_widget):
    """Create and return a button widget used to generate values for a field.

    Receives the generate callable and the target edit widget.
    """
    generate_callback = ui.thunk(_generate, generate_callable, edit_widget)
    generate_button = ui.MenuButton(
        ('field button', 'Click here to automatically generate'),
        generate_callback)
    return urwid.Columns([
        ('pack', generate_button),
        urwid.Text(' this value'),
    ])


def _create_buttons_grid_widget(choices, edit_widget):
    """Create and return a grid of button widgets.

    Buttons are associated with the given choices, and when clicked, udpate
    the given edit_widget's text.
    """
    callback = edit_widget.set_edit_text
    buttons = [
        ui.MenuButton(('field button', choice), ui.thunk(callback, choice))
        for choice in choices
    ]
    cell_width = max(button.base_widget.pack()[0] for button in buttons)
    return urwid.GridFlow(buttons, cell_width, 1, 0, 'left')


def _create_choices_widget(choices, required, edit_widget):
    """Create and return a choices widget.

    The widget displays the given choices for a specific form field. Clicking a
    choice updates the corresponding edit widget.
    """
    widgets = [urwid.Text('possible values are:')]
    buttons_grid = _create_buttons_grid_widget(choices, edit_widget)
    widgets.append(buttons_grid)
    if not required:
        button = ui.MenuButton(
            ('field button', 'left empty'),
            ui.thunk(edit_widget.set_edit_text, ''))
        widgets.append(urwid.Columns([
            ('pack', urwid.Text('but this field can also be ')), button,
        ]))
    help = urwid.Text(
        'click the choices to auto-fill the field with the standard options')
    widgets.append(help)
    return urwid.Pile(widgets)


def create_string_widget(field, value, error):
    """Create a string widget and return a tuple (widget, value_getter).

    Receives a Field instance (see quickstart.models.fields), the field value,
    and an error string (or None if the field has no errors).

    In the returned tuple, widget is a Urwid widget suitable for editing string
    values, and value_getter is a callable returning the value currently stored
    in the widget. The value_getter callable must be called without arguments.
    """
    if value is None:
        # Unset values are converted to empty strings.
        value = ''
    elif not isinstance(value, unicode):
        # We do not expect byte strings, and all other values are converted to
        # unicode strings.
        value = unicode(value)
    caption_class = 'highlight' if field.required else 'optional'
    caption = []
    widgets = []
    if error:
        caption.append(('error', '\N{BULLET} '))
        # Display the error message above the edit widget.
        widgets.append(urwid.Text(('error', error)))
    caption.append((caption_class, '{}: '.format(field.label)))
    edit_widget = urwid.Edit(edit_text=value)
    widget = urwid.Columns([('pack', urwid.Text(caption)), edit_widget])
    if field.readonly:
        # Disable the widget if the field is not editable.
        widgets.append(urwid.WidgetDisable(widget))
    else:
        widgets.append(urwid.AttrMap(widget, 'edit'))
    if field.help:
        # Display the field help message below the edit widget.
        widgets.append(urwid.Text(field.help))
    if not field.readonly:
        # Can we display suggestions for this field?
        suggestions = getattr(field, 'suggestions', ())
        if suggestions:
            widgets.append(
                _create_buttons_grid_widget(suggestions, edit_widget))
        # Can the value be automatically generated?
        generate_callable = getattr(field, 'generate', None)
        if generate_callable is not None:
            widgets.append(
                _create_generate_widget(generate_callable, edit_widget))
        # If the value must be in a range of choices, display the possible
        # choices as part of the help message.
        choices = getattr(field, 'choices', None)
        if choices is not None:
            choices_widget = _create_choices_widget(
                tuple(choices), field.required, edit_widget)
            widgets.append(choices_widget)
    if field.default is not None:
        widgets.append(
            urwid.Text('default if not set: {}'.format(field.default)))
    widgets.append(urwid.Divider())
    return urwid.Pile(widgets), edit_widget.get_edit_text


def create_bool_widget(field, value, error):
    """Create a boolean widget and return a tuple (widget, value_getter).

    Receives a Field instance (see quickstart.models.fields), the field value,
    and an error string (or None if the field has no errors).

    In the returned tuple, widget is a Urwid widget suitable for editing
    boolean values (a checkbox), and value_getter is a callable returning the
    value currently stored in the widget. The value_getter callable receives no
    arguments.
    """
    if value is None:
        # Unset values are converted to a more convenient value for the
        # checkbox (a boolean or a mixed state if allowed by the field).
        value = MIXED if field.allow_mixed else bool(field.default)
    label = ('highlight', field.label)
    widget = urwid.CheckBox(label, state=value, has_mixed=field.allow_mixed)
    widgets = []
    if error:
        # Display the error message above the checkbox.
        widgets.append(urwid.Text(('error', error)))
    if field.readonly:
        # Disable the widget if the field is not editable.
        widgets.append(urwid.WidgetDisable(widget))
    else:
        widgets.append(widget)
    if field.help:
        # Display the field help message below the checkbox.
        widgets.append(urwid.Text(field.help))
    widgets.append(urwid.Divider())

    def get_state():
        # Reconvert mixed value to None value.
        state = widget.get_state()
        return None if state == MIXED else state

    return urwid.Pile(widgets), get_state


def create_form(field_value_pairs, errors):
    """Create and return the form widgets for each field/value pair.

    Return a tuple (widgets, values_getter) in which:
        - widgets is a list if Urwid objects that can be used to build view
          contents (e.g. by wrapping them in a urwid.ListBox);
        - values_getter is a function returning a dictionary mapping field
          names to values. By calling the values_getter function it is always
          possible to retrieve the current new field values, even if they have
          been changed by the user.

    The field_value_pairs argument is a list of (field, value) tuples where
    field is a Field instance (see quickstart.models.fields) and value is
    the corresponding field's value.

    The errors argument is a dictionary mapping field names to error messages.
    Passing an empty dictionary means the form has no errors.
    """
    form = {}
    widgets = []
    if errors:
        # Inform the user that the form has errors that need to be fixed.
        num_errors = len(errors)
        msg = 'error' if num_errors == 1 else '{} errors'.format(num_errors)
        widgets.extend([
            urwid.Text(('error', 'please correct the {} below'.format(msg))),
            urwid.Divider(),
        ])
    # Build a widget and populate the form for each field/value pair.
    for field, value in field_value_pairs:
        error = errors.get(field.name)
        if field.field_type == 'bool':
            # Boolean values are represented as checkboxes.
            widget_factory = create_bool_widget
        else:
            # All the other field types are displayed as strings.
            widget_factory = create_string_widget
        widget, value_getter = widget_factory(field, value, error)
        widgets.append(widget)
        form[field.name] = value_getter
    return widgets, functools.partial(_get_data, form)


def _get_data(form):
    """Return a dictionary mapping the given form field names to values.

    This is done just calling all the value getters in the form.
    """
    return dict((key, value_getter()) for key, value_getter in form.items())


def create_actions(actions):
    """Return the control widgets based on the given actions.

    The actions arguments is as a sequence of (caption, callback) tuples. Those
    pairs are used to generate the clickable controls (MenuButton instances)
    used to manipulate the form.
    """
    return ui.create_controls(
        *(ui.MenuButton(caption, callback) for caption, callback in actions))
