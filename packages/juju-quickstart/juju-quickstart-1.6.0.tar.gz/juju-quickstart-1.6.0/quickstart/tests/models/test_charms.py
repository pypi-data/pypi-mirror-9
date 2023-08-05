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

"""Tests for the Juju Quickstart charms management."""

from __future__ import unicode_literals

import unittest

from quickstart.models import charms
from quickstart.tests import helpers


class TestParseUrl(helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_no_schema_error(self):
        # A ValueError is raised if the URL schema is missing.
        expected = 'charm URL has no schema: precise/juju-gui'
        with self.assert_value_error(expected):
            charms.parse_url('precise/juju-gui')

    def test_invalid_schema_error(self):
        # A ValueError is raised if the URL schema is not valid.
        expected = 'charm URL has invalid schema: http'
        with self.assert_value_error(expected):
            charms.parse_url('http:precise/juju-gui')

    def test_invalid_user_form_error(self):
        # A ValueError is raised if the user form is not valid.
        expected = 'charm URL has invalid user name form: jean-luc'
        with self.assert_value_error(expected):
            charms.parse_url('cs:jean-luc/precise/juju-gui')

    def test_invalid_user_name_error(self):
        # A ValueError is raised if the user name is not valid.
        expected = 'charm URL has invalid user name: jean:luc'
        with self.assert_value_error(expected):
            charms.parse_url('cs:~jean:luc/precise/juju-gui')

    def test_local_user_name_error(self):
        # A ValueError is raised if a user is specified on a local charm.
        expected = (
            'local charm URL with user name: '
            'local:~jean-luc/precise/juju-gui')
        with self.assert_value_error(expected):
            charms.parse_url('local:~jean-luc/precise/juju-gui')

    def test_invalid_form_error(self):
        # A ValueError is raised if the URL is not valid.
        expected = 'charm URL has invalid form: cs:~user/series/name/what-?'
        with self.assert_value_error(expected):
            charms.parse_url('cs:~user/series/name/what-?')

    def test_invalid_series_error(self):
        # A ValueError is raised if the series is not valid.
        expected = 'charm URL has invalid series: boo!'
        with self.assert_value_error(expected):
            charms.parse_url('cs:boo!/juju-gui-42')

    def test_no_revision_error(self):
        # A ValueError is raised if the charm revision is missing.
        expected = 'charm URL has no revision: cs:series/name'
        with self.assert_value_error(expected):
            charms.parse_url('cs:series/name')

    def test_invalid_revision_error(self):
        # A ValueError is raised if the charm revision is not valid.
        expected = 'charm URL has invalid revision: revision'
        with self.assert_value_error(expected):
            charms.parse_url('cs:series/name-revision')

    def test_invalid_name_error(self):
        # A ValueError is raised if the charm name is not valid.
        expected = 'charm URL has invalid name: not:valid'
        with self.assert_value_error(expected):
            charms.parse_url('cs:precise/not:valid-42')

    def test_success_with_user(self):
        # A charm URL including the user is correctly parsed.
        schema, user, series, name, revision = charms.parse_url(
            'cs:~who/precise/juju-gui-42')
        self.assertEqual('cs', schema)
        self.assertEqual('who', user)
        self.assertEqual('precise', series)
        self.assertEqual('juju-gui', name)
        self.assertEqual(42, revision)

    def test_success_without_user(self):
        # A charm URL not including the user is correctly parsed.
        schema, user, series, name, revision = charms.parse_url(
            'cs:trusty/django-1')
        self.assertEqual('cs', schema)
        self.assertEqual('', user)
        self.assertEqual('trusty', series)
        self.assertEqual('django', name)
        self.assertEqual(1, revision)

    def test_success_local_charm(self):
        # A local charm URL is correctly parsed.
        schema, user, series, name, revision = charms.parse_url(
            'local:saucy/wordpress-100')
        self.assertEqual('local', schema)
        self.assertEqual('', user)
        self.assertEqual('saucy', series)
        self.assertEqual('wordpress', name)
        self.assertEqual(100, revision)


class TestCharm(helpers.ValueErrorTestsMixin, unittest.TestCase):

    def make_charm(
            self, schema='cs', user='myuser', series='precise',
            name='juju-gui', revision=42):
        """Create and return a Charm instance."""
        return charms.Charm(schema, user, series, name, revision)

    def test_attributes(self):
        # All charm attributes are correctly stored.
        charm = self.make_charm()
        self.assertEqual('cs', charm.schema)
        self.assertEqual('myuser', charm.user)
        self.assertEqual('precise', charm.series)
        self.assertEqual('juju-gui', charm.name)
        self.assertEqual(42, charm.revision)

    def test_revision_as_string(self):
        # Revision is converted to an int.
        charm = self.make_charm(revision='47')
        self.assertEqual(47, charm.revision)

    def test_from_url(self):
        # A Charm can be instantiated from a charm URL.
        charm = charms.Charm.from_url('cs:~who/trusty/django-1')
        self.assertEqual('cs', charm.schema)
        self.assertEqual('who', charm.user)
        self.assertEqual('trusty', charm.series)
        self.assertEqual('django', charm.name)
        self.assertEqual(1, charm.revision)

    def test_from_url_without_user(self):
        # Official charm store URLs are properly handled.
        charm = charms.Charm.from_url('cs:saucy/django-123')
        self.assertEqual('cs', charm.schema)
        self.assertEqual('', charm.user)
        self.assertEqual('saucy', charm.series)
        self.assertEqual('django', charm.name)
        self.assertEqual(123, charm.revision)

    def test_from_url_local(self):
        # Local charms URLs are properly handled.
        charm = charms.Charm.from_url('local:precise/my-local-charm-42')
        self.assertEqual('local', charm.schema)
        self.assertEqual('', charm.user)
        self.assertEqual('precise', charm.series)
        self.assertEqual('my-local-charm', charm.name)
        self.assertEqual(42, charm.revision)

    def test_from_url_error(self):
        # A ValueError is raised by the from_url class method if the provided
        # URL is not a valid charm URL.
        expected = 'charm URL has invalid form: cs:not-a-charm-url'
        with self.assert_value_error(expected):
            charms.Charm.from_url('cs:not-a-charm-url')

    def test_string(self):
        # The string representation of a charm instance is its URL.
        charm = self.make_charm()
        self.assertEqual('cs:~myuser/precise/juju-gui-42', bytes(charm))

    def test_repr(self):
        # A charm instance is correctly represented.
        charm = self.make_charm()
        self.assertEqual(
            '<Charm: cs:~myuser/precise/juju-gui-42>', repr(charm))

    def test_charm_store_url(self):
        # A charm store URL is correctly returned.
        charm = self.make_charm(schema='cs')
        self.assertEqual('cs:~myuser/precise/juju-gui-42', charm.url())

    def test_local_url(self):
        # A local charm URL is correctly returned.
        charm = self.make_charm(schema='local', user='')
        self.assertEqual('local:precise/juju-gui-42', charm.url())

    def test_charm_store_charm(self):
        # The is_local method returns False for charm store charms.
        charm = self.make_charm(schema='cs')
        self.assertFalse(charm.is_local())

    def test_local_charm(self):
        # The is_local method returns True for local charms.
        charm = self.make_charm(schema='local')
        self.assertTrue(charm.is_local())
