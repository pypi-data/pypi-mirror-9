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

"""Tests for the Juju Quickstart CLI forms management."""

from __future__ import unicode_literals

import collections
import unittest

import mock
import urwid

from quickstart.cli import (
    forms,
    ui,
)
from quickstart.models import fields
from quickstart.tests.cli import helpers as cli_helpers


class TestGenerate(unittest.TestCase):

    def test_generation(self):
        # The text of the given widget is set to the return value of the given
        # callable.
        generate_callable = lambda: 'generated'
        mock_edit_widget = mock.Mock()
        forms._generate(generate_callable, mock_edit_widget)
        mock_edit_widget.set_edit_text.assert_called_once_with('generated')


class TestCreateGenerateWidget(unittest.TestCase):

    def test_widget_creation(self):
        # The generate widget is properly created and returned.
        generate_callable = lambda: 'generated'
        mock_edit_widget = mock.Mock()
        widget = forms._create_generate_widget(
            generate_callable, mock_edit_widget)
        # The generate button is the first widget in the urwid.Columns.
        button = widget.contents[0][0]
        cli_helpers.emit(button)
        mock_edit_widget.set_edit_text.assert_called_once_with('generated')


class ChoicesTestsMixin(object):
    """Helpers for inspecting the choices widget."""

    def get_buttons(self, choices_widget):
        """Return the MenuButton instances included in the choices_widget."""
        # The grid widget including choices is the second widget in the pile.
        grid = choices_widget.contents[1][0]
        buttons = [
            widget for widget, _ in grid.contents
            if isinstance(widget, ui.MenuButton)
        ]
        # Check if the unset button is present.
        columns_or_text = choices_widget.contents[2][0]
        if isinstance(columns_or_text, urwid.Columns):
            buttons.append(columns_or_text.contents[1][0])
        return buttons

    def assert_choices(self, expected_choices, choices_widget):
        """Ensure the given choices widget is well formed.

        The message displayed should equal the given expected_message.
        """
        obtained_choices = [
            cli_helpers.get_button_caption(button) for
            button in self.get_buttons(choices_widget)
        ]
        self.assertEqual(expected_choices, obtained_choices)


class TestCreateButtonsGridWidget(unittest.TestCase):

    def setUp(self):
        # Set up a mock edit widget and choices.
        self.mock_edit_widget = mock.Mock()
        self.choices = ['Kirk', 'Picard', 'Sisko']
        self.widget = forms._create_buttons_grid_widget(
            self.choices, self.mock_edit_widget)

    def get_buttons(self):
        """Return a list of buttons included in self.widget."""
        return [button for button, _ in self.widget.contents]

    def test_widget_structure(self):
        # The resulting widget is a urwid.GridFlow including all the expected
        # button widgets.
        self.assertIsInstance(self.widget, urwid.GridFlow)
        buttons = self.get_buttons()
        self.assertEqual(len(self.choices), len(buttons))
        self.assertEqual(
            self.choices, map(cli_helpers.get_button_caption, buttons))

    def test_button_click(self):
        # The given edit widget is updated when buttons are clicked.
        for button in self.get_buttons():
            choice = cli_helpers.get_button_caption(button)
            # Click the button.
            cli_helpers.emit(button)
            # Ensure the edit widget has been updated accordingly.
            self.mock_edit_widget.set_edit_text.assert_called_with(choice)


class TestCreateChoicesWidget(ChoicesTestsMixin, unittest.TestCase):

    def setUp(self):
        # Set up a mock edit widget and choices.
        self.mock_edit_widget = mock.Mock()
        self.choices = ['Kirk', 'Picard', 'Sisko']

    def test_widget_message(self):
        # The resulting widget includes all the choices.
        widget = forms._create_choices_widget(
            self.choices, True, self.mock_edit_widget)
        # The resulting pile widget is composed by choices and help message.
        self.assert_choices(self.choices, widget)
        help_widget = widget.contents[2][0]
        self.assertEqual(
            'click the choices to auto-fill the field with the '
            'standard options',
            help_widget.text)

    def test_widget_buttons(self):
        # The widget includes a button for each choice.
        widget = forms._create_choices_widget(
            self.choices, True, self.mock_edit_widget)
        buttons = self.get_buttons(widget)
        self.assertEqual(3, len(buttons))
        self.assertEqual(
            self.choices, map(cli_helpers.get_button_caption, buttons))

    def test_choice_click(self):
        # Clicking a choice updates the edit widget.
        widget = forms._create_choices_widget(
            self.choices, True, self.mock_edit_widget)
        buttons = self.get_buttons(widget)
        for button in buttons:
            choice = cli_helpers.get_button_caption(button)
            # Click the button.
            cli_helpers.emit(button)
            # Ensure the edit widget has been updated accordingly.
            self.mock_edit_widget.set_edit_text.assert_called_with(choice)

    def test_not_required(self):
        # If the field is not required, an option to unset the field is
        # displayed.
        widget = forms._create_choices_widget(
            self.choices, False, self.mock_edit_widget)
        self.assert_choices(self.choices + ['left empty'], widget)
        buttons = self.get_buttons(widget)
        # The last button is used to unset the edit widget.
        self.assertEqual(4, len(buttons))
        cli_helpers.emit(buttons[-1])
        self.mock_edit_widget.set_edit_text.assert_called_once_with('')


class TestCreateStringWidget(ChoicesTestsMixin, unittest.TestCase):

    def inspect_widget(self, widget, field):
        """Return a dict of sub-widgets composing the given string widget.

        The dictionary includes the following keys:

            - wrapper: the wrapper edit widget;
            - edit: the base edit widget;
            - caption: the caption text widget;
            - help: the help widget (or None if not present);
            - error: the error text widget (or None if not present);
            - suggestions: the suggested values grid (or None if not present);
            - generate: the generate text widget (or None if not present);
            - choices: the choices text widget (or None if not present);
            - default: the default text widget (or None if not present).
        """
        widgets = collections.defaultdict(lambda: None)
        # Retrieve the Pile contents ignoring the last Divider widget.
        contents = list(widget.contents)[:-1]
        first_widget = contents.pop(0)[0]
        if isinstance(first_widget, urwid.Text):
            # This is the error message.
            widgets.update({
                'error': first_widget,
                'wrapper': contents.pop(0)[0]
            })
        else:
            # The widget has no errors.
            widgets['wrapper'] = first_widget
        caption_attrs, edit_attrs = widgets['wrapper'].base_widget.contents
        widgets.update({
            'edit': edit_attrs[0],
            'caption': caption_attrs[0],
        })
        if field.help:
            widgets['help'] = contents.pop(0)[0]
        if hasattr(field, 'suggestions'):
            widgets['suggestions'] = contents.pop(0)[0]
        if hasattr(field, 'generate'):
            widgets['generate'] = contents.pop(0)[0]
        if hasattr(field, 'choices'):
            widgets['choices'] = contents.pop(0)[0]
        if field.default is not None:
            widgets['default'] = contents.pop(0)[0]
        return widgets

    def test_widget_structure(self):
        # The widget includes all the information about a field.
        field = fields.StringField(
            'first-name', label='first name', help='your first name',
            default='Jean')
        widget, _ = forms.create_string_widget(field, 'Luc', 'invalid name')
        widgets = self.inspect_widget(widget, field)
        # Since the field is not read-only, the widget is properly enabled.
        self.assertNotIsInstance(widgets['wrapper'], urwid.WidgetDisable)
        # The edit widget is set to the given value.
        self.assertEqual('Luc', widgets['edit'].get_edit_text())
        # The caption and help are properly set.
        self.assertEqual('\N{BULLET} first name: ', widgets['caption'].text)
        self.assertEqual('your first name', widgets['help'].text)
        # The error is displayed.
        self.assertEqual('invalid name', widgets['error'].text)
        # The field is not able to generate a value, and there are no choices
        # or suggestions.
        self.assertIsNone(widgets['generate'])
        self.assertIsNone(widgets['suggestions'])
        self.assertIsNone(widgets['choices'])
        # The default value is properly displayed.
        self.assertEqual('default if not set: Jean', widgets['default'].text)

    def test_value_getter(self):
        # The returned value getter function returns the current widget value.
        field = fields.StringField('first-name')
        widget, value_getter = forms.create_string_widget(field, 'Luc', None)
        edit = self.inspect_widget(widget, field)['edit']
        self.assertEqual('Luc', value_getter())
        # The value getter is lazy and always returns the current value.
        edit.set_edit_text('Jean-Luc')
        self.assertEqual('Jean-Luc', value_getter())

    def test_unset_value(self):
        # The initial value is set to an empty string if the field is unset.
        field = fields.StringField('first-name')
        _, value_getter = forms.create_string_widget(field, None, None)
        self.assertEqual('', value_getter())

    def test_value_not_a_string(self):
        # Non-string values are converted to unicode strings.
        field = fields.StringField('first-name')
        _, value_getter = forms.create_string_widget(field, 42, None)
        self.assertEqual('42', value_getter())

    def test_readonly_field(self):
        # The widget is disabled if the field is read-only.
        field = fields.StringField('first-name', readonly=True)
        widget, _ = forms.create_string_widget(field, 'Jean-Luc', None)
        wrapper = self.inspect_widget(widget, field)['wrapper']
        self.assertIsInstance(wrapper, urwid.WidgetDisable)

    def test_suggestions(self):
        # Suggested values, if present, are properly displayed below the edit
        # widget.
        field = fields.SuggestionsStringField(
            'captain', suggestions=('Kirk', 'Picard'))
        widget, _ = forms.create_string_widget(field, 'Luc', 'invalid name')
        suggestions = self.inspect_widget(widget, field)['suggestions']
        captions = [
            cli_helpers.get_button_caption(button)
            for button, attrs in suggestions.contents
        ]
        self.assertEqual(['Kirk', 'Picard'], captions)

    def test_autogenerated_field(self):
        # The widgets allows for automatically generating field values.
        field = fields.AutoGeneratedStringField('password')
        with mock.patch.object(field, 'generate', lambda: 'auto-generated!'):
            widget, value_getter = forms.create_string_widget(field, '', None)
        generate = self.inspect_widget(widget, field)['generate']
        # The generate button is the first widget in the urwid.Columns.
        generate_button = generate.contents[0][0]
        # Click the generate button, and ensure the value has been generated.
        cli_helpers.emit(generate_button)
        self.assertEqual('auto-generated!', value_getter())

    def test_choices(self):
        # Possible choices are properly displayed below the edit widget.
        field = fields.ChoiceField('captain', choices=('Kirk', 'Picard'))
        widget, _ = forms.create_string_widget(field, 'Luc', 'invalid name')
        choices = self.inspect_widget(widget, field)['choices']
        self.assert_choices(['Kirk', 'Picard', 'left empty'], choices)

    def test_choices_required_field(self):
        # Possible choices are properly displayed below the edit widget for
        # required fields.
        field = fields.ChoiceField(
            'captain', required=True, choices=('Janeway', 'Sisko'))
        widget, _ = forms.create_string_widget(field, 'Luc', 'invalid name')
        choices = self.inspect_widget(widget, field)['choices']
        self.assert_choices(['Janeway', 'Sisko'], choices)


class TestCreateBoolWidget(unittest.TestCase):

    def inspect_widget(self, widget, field):
        """Return a list of sub-widgets composing the given boolean widget.

        The sub-widgets are:
            - the checkbox widget;
            - the help widget (or None if not present);
            - the error text widget (or None if not present);
        """
        help = error = None
        # Retrieve the Pile contents ignoring the last Divider widget.
        contents = list(widget.contents)[:-1]
        first_widget = contents.pop(0)[0]
        if isinstance(first_widget, urwid.Text):
            # This is the error message.
            error = first_widget
            checkbox = contents.pop(0)[0]
        else:
            # The widget has no errors.
            checkbox = first_widget
        if field.help:
            help = contents.pop(0)[0]
        return checkbox, help, error

    def test_widget_structure(self):
        # The widget includes all the information about a field.
        field = fields.BoolField(
            'enabled', label='is enabled', help='something is enabled')
        widget, _ = forms.create_bool_widget(field, False, 'bad wolf')
        checkbox, help, error = self.inspect_widget(widget, field)
        # Since the field is not read-only, the widget is properly enabled.
        self.assertNotIsInstance(checkbox, urwid.WidgetDisable)
        # The checkbox widget is set to the given value.
        self.assertFalse(checkbox.get_state())
        # The help message is properly displayed.
        self.assertEqual('something is enabled', help.text)
        # The error is displayed.
        self.assertEqual('bad wolf', error.text)

    def test_value_getter(self):
        # The returned value getter function returns the current widget value.
        field = fields.BoolField('enabled')
        widget, value_getter = forms.create_bool_widget(field, True, None)
        checkbox = self.inspect_widget(widget, field)[0]
        self.assertTrue(value_getter())
        # The value getter is lazy and always returns the current value.
        checkbox.set_state(False)
        self.assertFalse(value_getter())

    def test_allow_mixed(self):
        # The checkbox has three possible states if allow_mixed is True.
        field = fields.BoolField('enabled', allow_mixed=True)
        widget, value_getter = forms.create_bool_widget(field, None, None)
        checkbox = self.inspect_widget(widget, field)[0]
        self.assertTrue(checkbox.has_mixed)
        self.assertEqual(forms.MIXED, checkbox.get_state())
        # A mixed value is converted to None when the value is retrieved.
        self.assertIsNone(value_getter())

    def test_mixed_not_allowed(self):
        # The checkbox can only be in a True/False state if the field's
        # allow_mixed is set to False.
        field = fields.BoolField('enabled', allow_mixed=False, default=True)
        widget, value_getter = forms.create_bool_widget(field, None, None)
        checkbox = self.inspect_widget(widget, field)[0]
        self.assertFalse(checkbox.has_mixed)
        # The default value is used if the input value is unset and mixed state
        # is not allowed.
        self.assertTrue(checkbox.get_state())
        # The retrieved value reflects the checkbox internal state.
        self.assertTrue(value_getter())

    def test_readonly_field(self):
        # The widget is disabled if the field is read-only.
        field = fields.BoolField('enabled', readonly=True)
        widget, _ = forms.create_bool_widget(field, False, None)
        checkbox = self.inspect_widget(widget, field)[0]
        self.assertIsInstance(checkbox, urwid.WidgetDisable)


class TestCreateForm(unittest.TestCase):

    field_value_pairs = (
        (fields.StringField('first-name'), 'Jean-Luc'),
        (fields.BoolField('enabled'), True),
    )

    def test_form_creation(self):
        # The create_form factory correctly creates and returns the form
        # widgets for each field/value pair provided.
        widgets, _ = forms.create_form(self.field_value_pairs, {})
        self.assertEqual(2, len(widgets))
        string_widget, bool_widget = widgets
        caption = string_widget.contents[0][0].base_widget.contents[0][0].text
        self.assertEqual('first-name: ', caption)
        checkbox_label = bool_widget.contents[0][0].label
        self.assertEqual('enabled', checkbox_label)

    def test_values_getter(self):
        # The returned values getter function returns the current form values.
        widgets, values_getter = forms.create_form(self.field_value_pairs, {})
        self.assertEqual(
            {'enabled': True, 'first-name': u'Jean-Luc'}, values_getter())
        # The values getter is lazy and always returns the current values.
        bool_widget = widgets[1]
        checkbox = bool_widget.contents[0][0]
        checkbox.set_state(False)
        self.assertEqual(
            {'enabled': False, 'first-name': u'Jean-Luc'}, values_getter())

    def test_error_message(self):
        # The user is asked to correct the form errors.
        errors = {'first-name': 'invalid name'}
        widgets, _ = forms.create_form(self.field_value_pairs, errors)
        message = widgets[0]
        self.assertEqual('please correct the error below', message.text)

    def test_multiple_error_messages(self):
        # The user is asked to correct multiple form errors.
        errors = {'first-name': 'invalid name', 'enabled': 'invalid value'}
        widgets, _ = forms.create_form(self.field_value_pairs, errors)
        message = widgets[0]
        self.assertEqual('please correct the 2 errors below', message.text)

    def test_errros(self):
        # Widgets are created passing the corresponding errors.
        errors = {'first-name': 'invalid name'}
        widgets, _ = forms.create_form(self.field_value_pairs, errors)
        # The first widget is the error message, the second is a divider.
        string_widget = widgets[2]
        error = string_widget.contents[0][0]
        self.assertEqual('invalid name', error.text)


class TestCreateActions(unittest.TestCase):

    def setUp(self):
        # Set up actions.
        self.clicked = []
        actions = [
            ('load', ui.thunk(self.clicked.append, 'load clicked')),
            ('save', ui.thunk(self.clicked.append, 'save clicked')),
        ]
        # Create the controls and retrieve the menu buttons.
        controls = forms.create_actions(actions)
        columns = controls.contents[1][0].base_widget
        self.buttons = [widget.base_widget for widget, _ in columns.contents]

    def test_resulting_controls(self):
        # A menu button is created for each action.
        self.assertEqual(2, len(self.buttons))
        load_button, save_button = self.buttons
        self.assertEqual('load', cli_helpers.get_button_caption(load_button))
        self.assertEqual('save', cli_helpers.get_button_caption(save_button))

    def test_callbacks(self):
        # The action callbacks are properly attached to each menu button.
        load_button, save_button = self.buttons
        cli_helpers.emit(load_button)
        self.assertEqual(['load clicked'], self.clicked)
        cli_helpers.emit(save_button)
        self.assertEqual(['load clicked', 'save clicked'], self.clicked)
