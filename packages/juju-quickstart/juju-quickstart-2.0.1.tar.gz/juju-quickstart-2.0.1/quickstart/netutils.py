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

import httplib
import logging
import socket
import urllib2


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


class NotFoundError(Exception):
    """Represent a 404 not found HTTP error."""


def urlread(url):
    """Open the given URL and return the page contents.

    Raise a NotFoundError if the request returns a 404 not found response.
    Raise an IOError if any other problems occur.
    """
    logging.debug('sending HTTP GET request to {}'.format(url))
    try:
        response = urllib2.urlopen(url)
    except urllib2.HTTPError as err:
        exception = NotFoundError if err.code == 404 else IOError
        raise exception(bytes(err))
    except urllib2.URLError as err:
        raise IOError(err.reason)
    except (httplib.HTTPException, socket.error) as err:
        raise IOError(bytes(err))
    contents = response.read()
    content_type = response.headers['content-type']
    charset = 'utf-8'
    if 'charset=' in content_type:
        sent_charset = content_type.split('charset=')[-1].strip()
        if sent_charset:
            charset = sent_charset
    return contents.decode(charset, 'ignore')
