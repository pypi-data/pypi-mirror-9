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

"""Tests for the Juju Quickstart Urwid application base handling."""

from __future__ import unicode_literals

from contextlib import contextmanager
import unittest

import mock
import urwid

from quickstart.cli import base
from quickstart.tests.cli import helpers as cli_helpers


class TestCheckEncoding(unittest.TestCase):

    @contextmanager
    def patch_urwid(self, supports_unicode=True):
        """Patch the urwid.set_encoding and urwid.supports_unicode calls.

        Ensure the mock functions are called once with the expected arguments.

        Make urwid.supports_unicode return the given supports_unicode value.
        """
        mock_supports_unicode = mock.Mock(return_value=supports_unicode)
        with mock.patch('urwid.set_encoding') as mock_set_encoding:
            with mock.patch('urwid.supports_unicode', mock_supports_unicode):
                yield
        mock_set_encoding.assert_called_once_with('utf-8')
        mock_supports_unicode.assert_called_once_with()

    def test_unicode_supported(self):
        # The utf-8 encoding is properly set and the function exits without
        # errors.
        with self.patch_urwid(supports_unicode=True):
            base._check_encoding()

    def test_unicode_not_supported(self):
        # If unicode is not supported, the program exits with an error.
        with self.patch_urwid(supports_unicode=False):
            with self.assertRaises(SystemExit) as context_manager:
                base._check_encoding()
        self.assertIn(
            b'Error: your terminal does not seem to support UTF-8 encoding.',
            bytes(context_manager.exception))


class TestMainLoop(unittest.TestCase):

    def setUp(self):
        # Create a loop instance.
        self.widget = urwid.ListBox(urwid.SimpleFocusListWalker([]))
        self.loop = base._MainLoop(self.widget)

    def test_initialization(self):
        # The customized loop is properly initialized, and it is an instance
        # of the Urwid loop.
        self.assertEqual(self.widget, self.loop.widget)
        self.assertIsInstance(self.loop, urwid.MainLoop)

    def test_unhandled_input(self):
        # The unhandled_input function can be set after the initialization.
        inputs = []
        self.loop.set_unhandled_input(inputs.append)
        self.loop.unhandled_input('ctrl z')
        self.assertEqual(['ctrl z'], inputs)

    def test_alarms(self):
        # It is possible to retrieve the list of event loop alarms.
        times_called = []
        self.assertEqual(0, len(self.loop.get_alarms()))
        callback = lambda *args: times_called.append(1)
        self.loop.set_alarm_in(3, callback)
        alarms = self.loop.get_alarms()
        self.assertEqual(1, len(alarms))
        alarms[0][1]()
        self.assertEqual(1, sum(times_called))


class TestSetupUrwidApp(cli_helpers.CliAppTestsMixin, unittest.TestCase):

    def setUp(self):
        # Set up the base Urwid application.
        self.loop, self.app = base.setup_urwid_app()

    def get_title_widget(self, loop):
        """Return the title widget given the application main loop."""
        # The frame is the main overlay's top widget.
        frame = loop.widget.top_w
        # Retrieve the header.
        header = frame.contents['header'][0]
        # The title widget is the first in the header pile.
        return header.contents[0][0].base_widget

    def get_contents_widget(self, loop):
        """Return the contents widget given the application main loop."""
        # The frame is the main overlay's top widget.
        frame = loop.widget.top_w
        # Retrieve the body.
        body = frame.contents['body'][0]
        # The contents widget is the body's original widget.
        return body.original_widget

    def _get_footer(self, loop):
        # The frame is the main overlay's top widget.
        frame = loop.widget.top_w
        # Retrieve the footer.
        return frame.contents['footer'][0]

    def get_status_widget(self, loop):
        """Return the status widget given the application main loop."""
        footer = self._get_footer(loop)
        # The status columns is the third widget (message, divider, status).
        columns = footer.contents[2][0].base_widget
        # The status widget is the second one (base status, status).
        return columns.contents[1][0]

    def get_message_widget(self, loop):
        """Return the message widget given the application main loop."""
        footer = self._get_footer(loop)
        # The message widget is the first one (message, divider, status).
        return footer.contents[0][0].base_widget

    def test_loop(self):
        # The returned loop is an instance of the base customized loop.
        self.assertIsInstance(self.loop, base._MainLoop)

    def test_app(self):
        # The returned app is the application named tuple
        self.assertIsInstance(self.app, base.App)

    def test_set_title(self):
        # The set_title API sets the application title.
        self.app.set_title('The Inner Light')
        title_widget = self.get_title_widget(self.loop)
        self.assertEqual('\nThe Inner Light', title_widget.text)

    def test_get_title(self):
        # The get_title API retrieves the application title.
        title_widget = self.get_title_widget(self.loop)
        title_widget.set_text('The Outer Space')
        self.assertEqual('The Outer Space', self.app.get_title())

    def test_set_contents(self):
        # The set_contents API changes the application main contents widget.
        text_widget = urwid.Text('my contents')
        self.app.set_contents(text_widget)
        contents_widget = self.get_contents_widget(self.loop)
        self.assertEqual('my contents', contents_widget.text)

    def test_get_contents(self):
        # The get_contents API returns the contents widget.
        contents_widget = self.get_contents_widget(self.loop)
        self.assertEqual(contents_widget, self.app.get_contents())

    def test_set_status(self):
        # The set_status API sets the status message displayed in the footer.
        self.app.set_status('press play on tape')
        status_widget = self.get_status_widget(self.loop)
        self.assertEqual('press play on tape', status_widget.text)

    def test_get_status(self):
        # The get_status API returns the current status message.
        status_widget = self.get_status_widget(self.loop)
        status_widget.set_text('hit space to continue')
        self.assertEqual('hit space to continue', self.app.get_status())

    def test_set_message(self):
        # The set_message API sets the message to be displayed in the
        # notification area.
        self.app.set_message('this will disappear')
        message_widget = self.get_message_widget(self.loop)
        self.assertEqual('this will disappear', message_widget.text)
        # An alarm is set to make this message disappear.
        alarms = self.loop.get_alarms()
        self.assertEqual(1, len(alarms))
        # Calling the callback makes the message go away.
        _, callback = alarms[0]
        callback()
        self.assertEqual('', message_widget.text)

    def test_get_message(self):
        # The get_message API returns the current notification message.
        message_widget = self.get_message_widget(self.loop)
        message_widget.set_text('42')
        self.assertEqual('42', self.app.get_message())

    def test_default_unhandled_input(self):
        # The default unhandled_input function is configured so that a
        # quickstart.cli.ui.AppExit exception is raised. The exception's
        # return value is None by default.
        return_value = self.get_on_exit_return_value(self.loop)
        self.assertIsNone(return_value)

    def test_set_return_value_on_exit(self):
        # It is possible to change the value returned by the AppExit exception
        # when the user quits the application using the exit shortcut.
        self.app.set_return_value_on_exit(42)
        return_value = self.get_on_exit_return_value(self.loop)
        self.assertEqual(42, return_value)
        # The value can be changed multiple times.
        self.app.set_return_value_on_exit([47, None])
        return_value = self.get_on_exit_return_value(self.loop)
        self.assertEqual([47, None], return_value)
