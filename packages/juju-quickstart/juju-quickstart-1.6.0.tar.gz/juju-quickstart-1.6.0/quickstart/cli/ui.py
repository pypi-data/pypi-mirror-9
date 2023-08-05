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

"""Juju Quickstart Urwid related utility objects."""

from __future__ import unicode_literals

import functools

import urwid


# Define the shortcut used to quit the interactive session.
EXIT_KEY = 'ctrl x'
# Define the color palette used by the Urwid application.
PALETTE = [
    # Class name, foreground color, background color.
    # See <http://excess.org/urwid/docs/reference/constants.html
    # foreground-and-background-colors>.
    (None, 'light gray', 'black'),
    ('active', 'light green', 'black'),
    ('active status', 'dark green', 'light gray'),
    ('dialog', 'dark gray', 'light gray'),
    ('dialog header', 'light gray,bold', 'dark blue'),
    ('control alert', 'light red', 'light gray'),
    ('controls', 'dark gray', 'light gray'),
    ('edit', 'white,underline', 'black'),
    ('error', 'light red', 'black'),
    ('error status', 'light red', 'light gray'),
    ('error selected', 'light red', 'dark blue'),
    ('field button', 'white,underline', 'black'),
    ('field button selected', 'white,underline', 'dark blue'),
    ('footer', 'black', 'light gray'),
    ('message', 'white', 'dark green'),
    ('header', 'white', 'dark magenta'),
    ('highlight', 'white', 'black'),
    ('line header', 'dark gray', 'dark magenta'),
    ('line footer', 'light gray', 'light gray'),
    ('optional', 'light magenta', 'black'),
    ('optional status', 'light magenta', 'light gray'),
    ('selected', 'white', 'dark blue'),
]
# Map attributes to new attributes to apply when the widget is selected.
FOCUS_MAP = {
    None: 'selected',
    'control alert': 'error selected',
    'error': 'error selected',
    'field button': 'field button selected',
    'highlight': 'selected',
}
# Define a default padding for the Urwid application.
padding = functools.partial(urwid.Padding, left=2, right=2)


class AppExit(Exception):
    """Used by views to stop the interactive execution returning a value."""

    def __init__(self, return_value=None):
        """Set the value to return to the view caller (default is None)."""
        self.return_value = return_value

    def __str__(self):
        return b'{}: {!r}'.format(self.__class__.__name__, self.return_value)


def exit_and_return(return_value):
    """Return a function that can be used as unhandled_input for an Urwid app.

    The resulting function terminates the interactive session with the given
    return_value when the user hits CTRL-x.
    """
    def unhandled_input(key):
        if key == EXIT_KEY:
            raise AppExit(return_value)
    return unhandled_input


def create_controls(*args):
    """Create a row of control widgets surrounded by line boxes."""
    controls = urwid.Columns([padding(urwid.LineBox(arg)) for arg in args])
    return urwid.Pile([
        urwid.Divider(top=1, bottom=1),
        urwid.AttrMap(controls, 'controls')
    ])


class MenuButton(urwid.Button):
    """A customized Urwid button widget.

    This behaves like a regular button, but also takes a callback that is
    called when the button is clicked.
    """

    def __init__(self, caption, callback):
        super(MenuButton, self).__init__('')
        urwid.connect_signal(self, 'click', callback)
        icon = urwid.SelectableIcon(caption, 0)
        # Replace the original widget: it seems ugly but it is Urwid idiomatic.
        self._w = urwid.AttrMap(icon, None, FOCUS_MAP)


def show_dialog(
        app, title, message, actions=None, dismissable=True,
        width=None, height=None):
    """Display an interactive modal dialog.

    This function receives the following arguments:
        - app: the App named tuple used to configure the current interactive
          session (see the quickstart.cli.base module);
        - title: the title of the message dialog;
        - message: the help message displayed in the dialog;
        - actions: the actions which can be executed from the dialog, as a
          sequence of (caption, callback) tuples. Those pairs are used to
          generate the clickable controls (MenuButton instances) displayed
          in the dialog;
        - dismissable: if set to True, a "cancel" button is prepended to the
          list of controls. Clicking the "cancel" button, the dialog just
          disappears without further changes to the state of the application;
        - width and height: optional dialog width and height as defined in
          Urwid, e.g. 'pack', 'relative' or the number of rows/columns.
          If not provided, the function tries to generate suitable defaults.

    Return a function that can be called to dismiss the dialog.
    """
    original_contents = app.get_contents()
    # Set up the dialog's header.
    header = urwid.Pile([
        urwid.Divider(),
        urwid.Text(title, align='center'),
        urwid.Divider(),
    ])
    # Set up the controls displayed in the dialog.
    if actions is None:
        controls = []
    else:
        controls = [
            MenuButton(caption, callback) for caption, callback in actions]
    # The dialog is removed by restoring the view original contents.
    dismiss = thunk(app.set_contents, original_contents)
    if dismissable:
        controls.insert(0, MenuButton('cancel', dismiss))
    # Create the listbox that replaces the original view contents.
    widgets = [
        urwid.AttrMap(header, 'dialog header'),
        urwid.Divider(),
        urwid.Text(message, align='center'),
        create_controls(*controls),
    ]
    listbox = urwid.ListBox(urwid.SimpleFocusListWalker(widgets))
    if width is None:
        # Calculate the dialog width: the max from the title/message length +
        # two padding spaces for each side.
        width = max(len(title), len(message)) + 4
    if height is None:
        # A height of eleven is usually enough for the dialog.
        height = 11
    contents = urwid.Overlay(
        urwid.AttrMap(listbox, 'dialog'), original_contents,
        align='center', width=width,
        valign='middle', height=height)
    app.set_contents(contents)
    return dismiss


class TabNavigationListBox(urwid.ListBox):
    """A ListBox supporting tab navigation."""

    key_conversion_map = {'tab': 'down', 'shift tab': 'up'}

    def keypress(self, size, key):
        """Override to convert tabs to up/down keys."""
        key = self.key_conversion_map.get(key, key)
        return super(TabNavigationListBox, self).keypress(size, key)


def thunk(function, *args, **kwargs):
    """Create and return a callable binding the given method and args/kwargs.

    This is useful when the given function is used as a signal subscriber, e.g.
    as a callback to be called when an Urwid signal is sent. In most cases, the
    widget which generated the event is sent as first argument to the callback.
    Moreover, urwid.connect_signal handles only one user argument.
    See <http://excess.org/urwid/docs/reference/signals.html>.

    This function helps when the callback does not require the original widget
    and/or when it instead requires more than one argument, e.g.:

        def save(contents, commit=False):
            ...

        button = MenuButton('save and commit', ui.thunk(save, contents, True))

    This example uses the MenuButton widget defined above in this module.
    """
    def callback(*ignored_args, **ignored_kwargs):
        return function(*args, **kwargs)
    return callback


class TimeoutText(object):
    """Wrap urwid.Text widget instances.

    The resulting widget, when set_text is called, displays text messages only
    for the given number of seconds.
    """

    def __init__(self, widget, seconds, set_alarm, remove_alarm):
        """Create the wrapper widget.

        Receives the text widget to be wrapped, the number of seconds before
        the message disappears, the functions used to set and to remove an
        alarm on the loop (usually loop.set_alarm_in and loop.remove_alarm).
        """
        self.original_widget = widget
        self.seconds = seconds
        self._set_alarm = set_alarm
        self._remove_alarm = remove_alarm
        self._handle = None

    def __getattr__(self, attr):
        """Allow access to the original widget's attributes."""
        return getattr(self.original_widget, attr)

    def set_text(self, text):
        """Set the text message on the original widget.

        Set up an alert that will clear the message after the given number of
        seconds. Remove any previously set alarms if required.
        """
        handle = self._handle
        if handle is not None:
            self._remove_alarm(handle)
        self.original_widget.set_text(text)
        self._handle = self._set_alarm(self.seconds, self._alarm_callback)

    def _alarm_callback(self, *args):
        """Remove the message from the original widget.

        This method is called by the alarm set up in self.set_text().
        """
        self.original_widget.set_text('')
        self._handle = None
