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

"""Juju Quickstart charms management."""

from __future__ import unicode_literals

import re


# The following regular expressions are the same used in juju-core: see
# http://bazaar.launchpad.net/~go-bot/juju-core/trunk/view/head:/charm/url.go.
valid_user = re.compile(r'^[a-z0-9][a-zA-Z0-9+.-]+$').match
valid_series = re.compile(r'^[a-z]+([a-z-]+[a-z])?$').match
valid_name = re.compile(r'^[a-z][a-z0-9]*(-[a-z0-9]*[a-z][a-z0-9]*)*$').match


def parse_url(url):
    """Parse the given charm URL.

    Return a tuple containing the charm URL fragments: schema, user, series,
    name and revision. Each fragment is a string except revision (int).

    Raise a ValueError with a descriptive message if the given URL is not a
    valid charm URL.
    """
    # Retrieve the schema.
    try:
        schema, remaining = url.split(':', 1)
    except ValueError:
        msg = 'charm URL has no schema: {}'.format(url)
        raise ValueError(msg.encode('utf-8'))
    if schema not in ('cs', 'local'):
        msg = 'charm URL has invalid schema: {}'.format(schema)
        raise ValueError(msg.encode('utf-8'))
    # Retrieve the optional user, the series, name and revision.
    parts = remaining.split('/')
    parts_length = len(parts)
    if parts_length == 3:
        user, series, name_revision = parts
        if not user.startswith('~'):
            msg = 'charm URL has invalid user name form: {}'.format(user)
            raise ValueError(msg.encode('utf-8'))
        user = user[1:]
        if not valid_user(user):
            msg = 'charm URL has invalid user name: {}'.format(user)
            raise ValueError(msg.encode('utf-8'))
        if schema == 'local':
            msg = 'local charm URL with user name: {}'.format(url)
            raise ValueError(msg.encode('utf-8'))
    elif parts_length == 2:
        user = ''
        series, name_revision = parts
    else:
        msg = 'charm URL has invalid form: {}'.format(url)
        raise ValueError(msg.encode('utf-8'))
    # Validate the series.
    if not valid_series(series):
        msg = 'charm URL has invalid series: {}'.format(series)
        raise ValueError(msg.encode('utf-8'))
    # Validate name and revision.
    try:
        name, revision = name_revision.rsplit('-', 1)
    except ValueError:
        msg = 'charm URL has no revision: {}'.format(url)
        raise ValueError(msg.encode('utf-8'))
    if not valid_name(name):
        msg = 'charm URL has invalid name: {}'.format(name)
        raise ValueError(msg.encode('utf-8'))
    try:
        revision = int(revision)
    except ValueError:
        msg = 'charm URL has invalid revision: {}'.format(revision)
        raise ValueError(msg.encode('utf-8'))
    return schema, user, series, name, revision


class Charm(object):
    """Represent the charm information stored in the charm URL."""

    def __init__(self, schema, user, series, name, revision):
        """Initialize the charm. Receives the URL fragments."""
        self.schema = schema
        self.user = user
        self.series = series
        self.name = name
        self.revision = int(revision)

    @classmethod
    def from_url(cls, url):
        """Given a charm URL, create and return a Charm instance.

        Raise a ValueError if the charm URL is not valid.
        """
        return cls(*parse_url(url))

    def __str__(self):
        """The string representation of a charm is its URL."""
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        """The unicode representation of a charm is its URL."""
        return self.url()

    def __repr__(self):
        return b'<Charm: {}>'.format(bytes(self))

    def url(self):
        """Return the charm URL."""
        user_part = '~{}/'.format(self.user) if self.user else ''
        return '{}:{}{}/{}-{}'.format(
            self.schema, user_part, self.series, self.name, self.revision)

    def is_local(self):
        """Return True if this is a local charm, False otherwise."""
        return self.schema == 'local'
