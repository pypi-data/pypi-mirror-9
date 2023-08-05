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

"""Test helpers for the Juju Quickstart CLI infrastructure."""

from __future__ import unicode_literals

import urwid

from quickstart.cli import ui


class CliAppTestsMixin(object):
    """Helper methods to test Quickstart CLI applications."""

    def get_on_exit_return_value(self, loop):
        """Return the value returned by the application when the user quits."""
        with self.assertRaises(ui.AppExit) as context_manager:
            loop.unhandled_input(ui.EXIT_KEY)
        return context_manager.exception.return_value


def get_button_caption(button):
    """Return the button caption as a string."""
    return button._w.original_widget.text


def emit(widget):
    """Emit the first signal associated withe the given widget.

    This is usually invoked to click buttons.
    """
    # Retrieve the first signal name (usually is 'click').
    signal_name = widget.signals[0]
    urwid.emit_signal(widget, signal_name, widget)


def inspect_dialog(contents):
    """Inspect the widgets composing the dialog.

    Return a tuple (title_widget, messaqe_widget, buttons) where:
        - title_widget is the Text widget displaying the dialog title;
        - message_widget is the Text widget displaying the dialog message;
        - buttons is a list of MenuButton widgets included in the dialog.
    """
    listbox = contents.top_w.base_widget
    header, _, message_widget, controls = listbox.body
    # The title widget is the second one in the header Pile.
    title_widget = header.base_widget.contents[1][0]
    # The button columns is the second widget in the Pile.
    columns = controls.contents[1][0].base_widget
    buttons = [content[0].base_widget for content in columns.contents]
    return title_widget, message_widget, buttons


def keypress(widget, key):
    """Simulate a key press on the given widget."""
    # Pass to the keypress method an arbitrary size.
    size = (42, 42)
    widget.keypress(size, key)
