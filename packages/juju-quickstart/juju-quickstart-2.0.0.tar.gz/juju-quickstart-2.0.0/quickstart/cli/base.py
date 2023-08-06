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

"""Juju Quickstart Urwid application base handling.

A collection of objects which help in building a Quickstart CLI application
skeleton. Views use these functions to set up the Urwid top widget and to start
the application main loop.

See the quickstart.cli.views module docstring for further details.
"""

from __future__ import unicode_literals

from collections import namedtuple
import sys

import urwid

from quickstart.cli import ui


# Define the application as a named tuple of callables.
App = namedtuple(
    'App', [
        'set_title', 'get_title',
        'set_contents', 'get_contents',
        'set_status', 'get_status',
        'set_message', 'get_message',
        'set_return_value_on_exit',
    ],
)


def _check_encoding():
    """Set the Urwid global byte encoding to utf-8.

    Exit the application if, for some reasons, the change does not have effect.
    """
    urwid.set_encoding('utf-8')
    if not urwid.supports_unicode():
        # Note: the following message must only include ASCII characters.
        msg = (
            'Error: your terminal does not seem to support UTF-8 encoding.\n'
            'Please check your locale settings.\n'
            'On Ubuntu, running the following might fix the problem:\n'
            '  sudo locale-gen en_US.UTF-8\n'
            '  sudo dpkg-reconfigure locales'
        )
        sys.exit(msg.encode('ascii'))


class _MainLoop(urwid.MainLoop):
    """A customized Urwid loop.

    Allow for setting the unhandled_input callable after the loop
    initialization.
    """

    def set_unhandled_input(self, unhandled_input):
        """Set the unhandled_input callable.

        The passed unhandled_input is a callable called when input is not
        handled by the application top widget.
        """
        self._unhandled_input = unhandled_input

    def get_alarms(self):
        """Return all the alarms set for this loop.

        Improves the level of event loop introspection so that code and tests
        can easily access the alarms list.

        The alarms list is a sequence of (time, callback) tuples.
        """
        return self.event_loop._alarms


def setup_urwid_app():
    """Configure a Urwid application suitable for being used by views.

    Build the Urwid top widget and instantiate a main loop. The top widget
    is basically a frame, composed by a header, some contents, and a footer.
    This application skeleton is Quickstart branded, and exposes functions
    that can be used by views to change the contents of the frame.

    Return a tuple (loop, app) where loop is the interactive session main loop
    (ready to be started invoking loop.run()) and app is a named tuple of
    callables exposing an API to be used by views to customize the application.

    The API exposed by app is limited by design, and includes:

        - set_title(text): set/change the title displayed in the application
          header (e.g.: app.set_title('my title'));
        - get_title(): return the current application title;

        - set_contents(widget): set/change the application body contents. A
          Urwid ListBox widget instance is usually provided, which replaces the
          current application contents;
        - get_contents(): return the current application contents widget;

        - set_status(text): set/change the status text displayed in the
          application footer (e.g.: set_status('press play on tape')). The
          status message can also be passed as a (style, text) tuple, as usual
          in Urwid code, e.g.: app.set_status(('error', 'error message'));
        - get_status(): return the current status message;

        - set_message(text): set/change a notification message, which is
          displayed in the footer for a couple of seconds before disappearing;
        - get_message(): return the message currently displayed in the
          notifications area;

        - set_return_value_on_exit(value): set the value to be encapsulated
          in the AppExit exception raised when the user quits the application
          with the exit shortcut. See the quickstart.cli.views module docstring
          for more information about this functionality.
    """
    _check_encoding()
    # Set up the application header.
    title = urwid.Text('\npreparing...')
    header_line = urwid.Divider('\N{LOWER ONE QUARTER BLOCK}')
    header = urwid.Pile([
        urwid.AttrMap(ui.padding(title), 'header'),
        urwid.AttrMap(header_line, 'line header'),
        urwid.Divider(),
    ])
    # Set up the application default contents.
    # View code is assumed to replace the placeholder widget using
    # app.set_contents(widget).
    placeholder = urwid.ListBox(urwid.SimpleFocusListWalker([]))
    contents = ui.padding(urwid.AttrMap(placeholder, None))

    def set_contents(widget):
        contents.original_widget = widget

    # Set up the application footer.
    # The CTRL-x shortcut is automatically set up by views.show().
    message = urwid.Text('', align='center')
    base_status = urwid.Text('^X exit ')
    status = urwid.Text('')
    status_columns = urwid.Columns([('pack', base_status), status])
    footer_line = urwid.Divider('\N{UPPER ONE EIGHTH BLOCK}')
    footer = urwid.Pile([
        message,
        urwid.Divider(),
        urwid.AttrMap(ui.padding(status_columns), 'footer'),
        urwid.AttrMap(footer_line, 'line footer'),
    ])
    # Compose the components in a frame, and set up the top widget. The top
    # widget is the topmost widget used for painting the screen.
    page = urwid.Frame(contents, header=header, footer=footer)
    top_widget = urwid.Overlay(
        page, urwid.SolidFill('\N{MEDIUM SHADE}'),
        align='center', width=('relative', 90),
        valign='middle', height=('relative', 90),
        min_width=78, min_height=20)
    # Instantiate the Urwid main loop.
    loop = _MainLoop(
        top_widget, palette=ui.PALETTE,
        unhandled_input=ui.exit_and_return(None))
    # Add a timeout to the notification message.
    timeout_message = ui.TimeoutText(
        message, 3, loop.set_alarm_in, loop.remove_alarm)

    # Allow views to set the value returned when the user quits the session.
    def set_return_value_on_exit(return_value):
        unhandled_input = ui.exit_and_return(return_value)
        loop.set_unhandled_input(unhandled_input)

    # Create the App named tuple. If, in the future, we have a view that
    # requires additional capabilities or API access, this is the place to add
    # those.
    app = App(
        set_title=lambda msg: title.set_text('\n{}'.format(msg)),
        get_title=lambda: title.text.lstrip(),
        set_contents=set_contents,
        get_contents=lambda: contents.original_widget,
        set_status=lambda msg: status.set_text(msg),
        get_status=lambda: status.text,
        set_message=lambda msg: timeout_message.set_text(('message', msg)),
        get_message=lambda: timeout_message.text,
        set_return_value_on_exit=set_return_value_on_exit,
    )
    return loop, app
