# This file is part of the Juju Quickstart Plugin, which lets users set up a
# Juju environment in very few steps (https://launchpad.net/juju-quickstart).
# Copyright (C) 2013-2014 Canonical Ltd.
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

"""Juju Quickstart is a Juju plugin which allows for easily setting up a Juju
environment in very few steps. The environment is bootstrapped and set up so
that it can be managed using a Web interface (the Juju GUI).
"""

from __future__ import unicode_literals


FEATURES = """
Features include the following:

* New users are guided, as needed, to install Juju, set up SSH keys, and
  configure it for first use.
* Juju environments can be created and managed from a command line interactive
  session.
* The Juju GUI is automatically installed, adding no additional machines
  (installing on an existing state server when possible).
* Bundles can be deployed, from local files, HTTP(S) URLs, or the charm store,
  so that a complete topology of services can be set up in one simple command.
* Quickstart ends by opening the browser and automatically logging the user
  into the Juju GUI.
* Users with a running Juju environment can run the quickstart command again to
  simply re-open the GUI without having to find the proper URL and password.

To start Juju Quickstart, run the following:

    juju-quickstart [-i]

Once Juju has been installed, the command can also be run as a juju plugin,
without the hyphen ("juju quickstart").
"""
VERSION = (2, 0, 0)


def get_version():
    """Return the Juju Quickstart version as a string."""
    return '.'.join(map(unicode, VERSION))
