# This file is part of the Juju Quickstart Plugin, which lets users set up a
# Juju environment in very few steps (https://launchpad.net/juju-quickstart).
# Copyright (C) 2013 Canonical Ltd.
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

"""Tests for the Juju Quickstart Urwid related utility objects."""

from __future__ import unicode_literals

import unittest

import mock
import urwid

from quickstart.cli import (
    base,
    ui,
)
from quickstart.tests.cli import helpers as cli_helpers


class TestAppExit(unittest.TestCase):

    def test_no_return_value(self):
        # The exception accepts a return value argument.
        exception = ui.AppExit(42)
        self.assertEqual(42, exception.return_value)

    def test_return_value(self):
        # The exception's return value defaults to None.
        exception = ui.AppExit()
        self.assertIsNone(exception.return_value)

    def test_string_representation(self):
        # The exception is correctly represented as a byte string.
        exception = ui.AppExit(42)
        str_exception = str(exception)
        self.assertIsInstance(str_exception, bytes)
        self.assertEqual(b'AppExit: 42', str_exception)


class TestExitAndReturn(unittest.TestCase):

    def test_app_exit(self):
        # The function returned raises an AppExit error if CTRL-x is passed.
        function = ui.exit_and_return(42)
        with self.assertRaises(ui.AppExit) as context_manager:
            function(ui.EXIT_KEY)
        self.assertEqual(42, context_manager.exception.return_value)

    def test_unhandled(self):
        # Passing other keys, the resulting function is a no-op.
        function = ui.exit_and_return(42)
        self.assertIsNone(function('alt z'))


class TestCreateControls(unittest.TestCase):

    def test_resulting_pile(self):
        # The resulting pile is properly structured: it includes a columns
        # widget containing the provided widgets.
        widget0 = urwid.Text('w0')
        widget1 = urwid.Text('w1')
        pile = ui.create_controls(widget0, widget1)
        divider_contents, columns_contents = pile.contents
        self.assertIsInstance(divider_contents[0], urwid.Divider)
        columns = columns_contents[0].original_widget
        widgets = [content[0].base_widget for content in columns.contents]
        self.assertIs(widget0, widgets[0])
        self.assertIs(widget1, widgets[1])


class TestMenuButton(unittest.TestCase):

    def test_caption(self):
        # The button's caption is properly set up.
        button = ui.MenuButton('my caption', mock.Mock())
        self.assertEqual('my caption', button._w.base_widget.text)

    def test_signals(self):
        # The given callback is called when the click signal is emitted.
        callback = mock.Mock()
        button = ui.MenuButton('my caption', callback)
        urwid.emit_signal(button, 'click', button)
        callback.assert_called_once_with(button)


class TestShowDialog(cli_helpers.CliAppTestsMixin, unittest.TestCase):

    def setUp(self):
        # Set up the base Urwid application.
        _, self.app = base.setup_urwid_app()
        self.original_contents = self.app.get_contents()

    def test_dialog_rendering(self):
        # The dialog is correctly displayed without additional controls.
        ui.show_dialog(self.app, 'my title', 'my message')
        contents = self.app.get_contents()
        self.assertIsNot(contents, self.original_contents)
        title_widget, message_widget, buttons = cli_helpers.inspect_dialog(
            contents)
        self.assertEqual('my title', title_widget.text)
        self.assertEqual('my message', message_widget.text)
        # The dialog only includes the "cancel" button.
        self.assertEqual(1, len(buttons))
        caption = cli_helpers.get_button_caption(buttons[0])
        self.assertEqual('cancel', caption)

    def test_dialog_cancel_action(self):
        # A dialog can be properly dismissed clicking the cancel button.
        ui.show_dialog(self.app, 'my title', 'my message')
        contents = self.app.get_contents()
        buttons = cli_helpers.inspect_dialog(contents)[2]
        cancel_button = buttons[0]
        cli_helpers.emit(cancel_button)
        # The original contents have been restored.
        self.assertIs(self.original_contents, self.app.get_contents())

    def test_dialog_customized_actions(self):
        # A button is displayed for each customized action provided.
        performed = []
        actions = [
            ('push me', ui.thunk(performed.append, 'push')),
            ('pull me', ui.thunk(performed.append, 'pull')),
        ]
        ui.show_dialog(self.app, 'my title', 'my message', actions=actions)
        contents = self.app.get_contents()
        buttons = cli_helpers.inspect_dialog(contents)[2]
        # Three buttons are displayed: "cancel", "push me" and "pull me".
        self.assertEqual(3, len(buttons))
        captions = [
            cli_helpers.get_button_caption(button) for button in buttons]
        self.assertEqual(['cancel', 'push me', 'pull me'], captions)
        push, pull = buttons[1:]
        # Click the "push me" button.
        cli_helpers.emit(push)
        self.assertEqual(['push'], performed)
        # Click the "pull me" button two times.
        cli_helpers.emit(pull)
        cli_helpers.emit(pull)
        self.assertEqual(['push', 'pull', 'pull'], performed)

    def test_not_dismissable(self):
        # The cancel button is not present if the dialog is not dismissable.
        actions = [('push me', lambda *args: None)]
        ui.show_dialog(
            self.app, 'my title', 'my message',
            actions=actions, dismissable=False)
        contents = self.app.get_contents()
        buttons = cli_helpers.inspect_dialog(contents)[2]
        # Only the "push me" button is displayed.
        self.assertEqual(1, len(buttons))
        caption = cli_helpers.get_button_caption(buttons[0])
        self.assertEqual('push me', caption)


class TestTabNavigationListBox(unittest.TestCase):

    def setUp(self):
        # Set up a TabNavigationListBox.
        self.widgets = [urwid.Edit(), urwid.Edit()]
        self.listbox = ui.TabNavigationListBox(
            urwid.SimpleFocusListWalker(self.widgets))

    def test_widgets(self):
        # The listbox includes the provided widgets.
        self.assertEqual(self.widgets, list(self.listbox.body))

    def test_tab_navigation(self):
        # The next widget is selected when tab is pressed.
        self.assertEqual(0, self.listbox.focus_position)
        cli_helpers.keypress(self.listbox, 'tab')
        self.assertEqual(1, self.listbox.focus_position)

    def test_shift_tab_navigation(self):
        # The previous widget is selected when shift+tab is pressed.
        self.listbox.set_focus(1)
        cli_helpers.keypress(self.listbox, 'shift tab')
        self.assertEqual(0, self.listbox.focus_position)


class TestThunk(unittest.TestCase):

    widget = 'test-widget'

    def test_no_args(self):
        # A callback can be set up without arguments.
        function = mock.Mock()
        thunk_function = ui.thunk(function)
        thunk_function(self.widget)
        function.assert_called_once_with()

    def test_args(self):
        # It is possible to bind arguments to the callback function.
        function = mock.Mock()
        thunk_function = ui.thunk(function, 'arg1', 'arg2')
        thunk_function(self.widget)
        function.assert_called_once_with('arg1', 'arg2')

    def test_return_value(self):
        # The closure returns the value returned by the original callback.
        sqr = lambda value: value * value
        thunk_function = ui.thunk(sqr, 3)
        self.assertEqual(9, thunk_function(self.widget))


class TestTimeoutText(unittest.TestCase):

    def setUp(self):
        # Set up a timeout text widget.
        self.original_widget = urwid.Text('original contents')
        self.loop = base._MainLoop(None)
        self.wrapper = ui.TimeoutText(
            self.original_widget, 42,
            self.loop.set_alarm_in, self.loop.remove_alarm)

    def test_attributes(self):
        # The original widget and the timeout seconds are accessible from the
        # wrapper.
        self.assertEqual(self.original_widget, self.wrapper.original_widget)
        self.assertEqual(42, self.wrapper.seconds)

    def test_original_attributes(self):
        # The original widget attributes can be accessed from the wrapper.
        self.assertEqual('original contents', self.wrapper.text)
        self.assertEqual(('original contents', []), self.wrapper.get_text())

    def test_set_timeout(self):
        # When setting text on a timeout text widget, am alarm is set up. The
        # alarm clears the text after the given number of seconds.
        self.wrapper.set_text('this will disappear')
        self.assertEqual('this will disappear', self.wrapper.text)
        alarms = self.loop.get_alarms()
        self.assertEqual(1, len(alarms))
        # Calling the callback makes the message go away.
        _, callback = alarms[0]
        callback()
        self.assertEqual('', self.wrapper.text)

    def test_update_timeout(self):
        # The alarm is updated when setting text multiple time.
        self.wrapper.set_text('this will disappear')
        timeout, _ = self.loop.get_alarms()[0]
        self.wrapper.set_text('and this too')
        alarms = self.loop.get_alarms()
        self.assertEqual(1, len(alarms))
        new_timeout, _ = alarms[0]
        # The new timeout is more far away in the future.
        self.assertGreater(new_timeout, timeout)
