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

"""Juju Quickstart utilities for supporting MAAS."""

from __future__ import unicode_literals

import logging
import os

from quickstart import (
    settings,
    utils,
)


def cli_available():
    """Report whether the MAAS CLI is available on the system."""
    path = settings.MAAS_CMD
    return os.path.isfile(path) and os.access(path, os.X_OK)


def get_api_info():
    """Return API info about the first logged in MAAS remote API.

    The info is returned as a tuple including the API name, the MAAS server
    address and the MAAS OAuth API key.

    Return None if no authenticated API is found.
    """
    retcode, output, error = utils.call(settings.MAAS_CMD, 'list')
    if retcode:
        # The MAAS CLI command failed. This is not supposed to happen, but
        # also not critical from the quickstart process perspective.
        logging.warn('unable to list MAAS remote APIs: ' + error)
        return None
    if not output:
        # No logged in remote API found.
        return None
    try:
        name, api_address, api_key = output.splitlines()[0].split()
    except ValueError:
        # The MAAS CLI returned an unexpected response.
        logging.warn('unexpected response from MAAS CLI: ' + output)
        return None
    return name, api_address.split('/api/')[0], api_key
