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

"""Juju Quickstart command line interface management.

The functions and objects included in this package can be used to build
rich command line interfaces using the Urwid console interface library
(see <http://excess.org/urwid/>).

This package is organized in several modules:
    - base: the base pieces used to set up Urwid applications;
    - views: view functions responsible for showing specific contents in the
      context of a Urwid app;
    - ui: Urwid related utility objects, including callback wrappers,
      customized widgets and style specific helpers.

Client code usually starts a Quickstart terminal application calling
views.show() with the view to display along with the view required arguments.
See the quickstart.cli.views module docstring for further details.
"""
