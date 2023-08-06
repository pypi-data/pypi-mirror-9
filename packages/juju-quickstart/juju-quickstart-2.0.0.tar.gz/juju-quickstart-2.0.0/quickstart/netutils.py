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

"""Juju Quickstart network utility functions."""

from __future__ import unicode_literals

import json
import httplib
import logging
import socket
import urllib2

from quickstart import settings


def check_resolvable(hostname):
    """Check that the hostname can be resolved to a numeric IP address.

    Return an error message if the address cannot be resolved.
    """
    try:
        address = socket.gethostbyname(hostname)
    except socket.error as err:
        return bytes(err).decode('utf-8')
    logging.debug('{} resolved to {}'.format(
        hostname, address.decode('utf-8')))
    return None


def check_listening(address, timeout=3):
    """Check that the given address is listening and accepts connections.

    The address must be specified as a "host:port" string.
    Use the given socket timeout in seconds.

    Return an error message if connecting to the address fails.
    """
    try:
        host, port = address.split(":")
        sock = socket.create_connection((host, int(port)), timeout)
    except (socket.error, TypeError, ValueError) as err:
        return 'cannot connect to {}: {}'.format(
            address, bytes(err).decode('utf-8'))
    # Ignore all possible connection close exceptions.
    try:
        sock.close()
    except:
        pass
    return None


def get_charm_url(series):
    """Return the charm URL of the latest Juju GUI charm revision.

    Raise an IOError if any problems occur connecting to the API endpoint.
    Raise a ValueError if the API returns invalid data.
    """
    url = '{}{}/{}/meta/id'.format(
        settings.CHARMSTORE_API, series, settings.JUJU_GUI_CHARM_NAME)
    data = json.loads(urlread(url))
    charm_url = data.get('Id')
    if charm_url is None:
        raise ValueError(b'unable to find the charm URL')
    return charm_url


def urlread(url):
    """Open the given URL and return the page contents.

    Raise an IOError if any problems occur.
    """
    try:
        response = urllib2.urlopen(url)
    except urllib2.URLError as err:
        raise IOError(err.reason)
    except (httplib.HTTPException, socket.error, urllib2.HTTPError) as err:
        raise IOError(bytes(err))
    contents = response.read()
    content_type = response.headers['content-type']
    charset = 'utf-8'
    if 'charset=' in content_type:
        sent_charset = content_type.split('charset=')[-1].strip()
        if sent_charset:
            charset = sent_charset
    return contents.decode(charset, 'ignore')
