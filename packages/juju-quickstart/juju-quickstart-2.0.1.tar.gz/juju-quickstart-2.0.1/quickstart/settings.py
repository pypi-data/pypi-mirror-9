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

"""Juju Quickstart settings."""

from __future__ import unicode_literals

import collections
import os

# Platforms.
LINUX_APT = object()
LINUX_RPM = object()
LINUX_UNKNOWN = object()
OSX = object()
UNKNOWN_PLATFORM = object()
WINDOWS = object()

# The base charm store API URL containing information about charms and bundles.
CHARMSTORE_API = 'https://api.jujucharms.com/charmstore/v4/'

# The default Juju GUI charm URLs for each supported series. Used when it is
# not possible to retrieve the charm URL from the charm store API, e.g. due to
# temporary connection/charm store errors.
# Keep this list sorted by release date (older first).
DEFAULT_CHARM_URLS = collections.OrderedDict((
    ('precise', 'cs:precise/juju-gui-108'),
    ('trusty', 'cs:trusty/juju-gui-21'),
))

# The quickstart app short description.
DESCRIPTION = 'set up a Juju environment (including the GUI) in very few steps'

# The URL of jujucharms.com, the home of Juju.
JUJUCHARMS_URL = 'https://jujucharms.com/'

# The path to the Juju command, based on platform.
JUJU_CMD_PATHS = {
    'default': '/usr/bin/juju',
    OSX: '/usr/local/bin/juju',
}

# Juju packages to install per platform.
JUJU_PACKAGES = {
    LINUX_APT: ('juju-core', 'juju-local'),
    OSX: ('juju', ),
}

# The possible values for the environments.yaml default-series field.
JUJU_DEFAULT_SERIES = (
    'precise', 'quantal', 'raring', 'saucy', 'trusty', 'utopic', 'vivid')

# Retrieve the current juju-core home.
JUJU_HOME = os.getenv('JUJU_HOME', '~/.juju')

# The name of the Juju GUI charm.
JUJU_GUI_CHARM_NAME = 'juju-gui'

# The name of the Juju GUI service.
JUJU_GUI_SERVICE_NAME = JUJU_GUI_CHARM_NAME

# The set of series supported by the Juju GUI charm.
JUJU_GUI_SUPPORTED_SERIES = tuple(DEFAULT_CHARM_URLS.keys())

# The minimum Juju version supported by Juju Quickstart,
JUJU_SUPPORTED_VERSION = (1, 18, 1)

# The path to the MAAS command line interface.
MAAS_CMD = '/usr/bin/maas'

# The minimum Juju GUI charm revision supporting bundle deployments, for each
# supported series. Assume not listed series to always support bundles.
MINIMUM_REVISIONS_FOR_BUNDLES = collections.defaultdict(
    lambda: 0, {'precise': 80})

# The minimum Juju GUI charm revision supporting the new Juju API endpoints
# including the environment UUID. Assume not listed series to always support
# new endpoints.
MINIMUM_REVISIONS_FOR_NEW_API_ENDPOINT = collections.defaultdict(
    lambda: 0, {'precise': 107, 'trusty': 19})
