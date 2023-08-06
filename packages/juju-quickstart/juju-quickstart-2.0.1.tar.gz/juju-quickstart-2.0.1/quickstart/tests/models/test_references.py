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

"""Tests for the Juju Quickstart charm and bundle references management."""

from __future__ import unicode_literals

import unittest

from quickstart import settings
from quickstart.models import references
from quickstart.tests import helpers


def make_reference(
        schema='cs', user='myuser', series='precise', name='juju-gui',
        revision=42):
    """Create and return a Reference instance."""
    return references.Reference(schema, user, series, name, revision)


class TestReference(unittest.TestCase):

    def test_attributes(self):
        # All reference attributes are correctly stored.
        ref = make_reference()
        self.assertEqual('cs', ref.schema)
        self.assertEqual('myuser', ref.user)
        self.assertEqual('precise', ref.series)
        self.assertEqual('juju-gui', ref.name)
        self.assertEqual(42, ref.revision)

    def test_revision_as_string(self):
        # The reference revision is converted to an int.
        ref = make_reference(revision='47')
        self.assertEqual(47, ref.revision)

    def test_string(self):
        # The string representation of a reference is its URL.
        tests = (
            (make_reference(),
             'cs:~myuser/precise/juju-gui-42'),
            (make_reference(schema='local'),
             'local:~myuser/precise/juju-gui-42'),
            (make_reference(user=''),
             'cs:precise/juju-gui-42'),
            (make_reference(user='dalek', revision=None, series='bundle'),
             'cs:~dalek/bundle/juju-gui'),
            (make_reference(name='django', series='vivid', revision=0),
             'cs:~myuser/vivid/django-0'),
            (make_reference(user='', revision=None),
             'cs:precise/juju-gui'),
        )
        for ref, expected_value in tests:
            self.assertEqual(expected_value, bytes(ref))

    def test_repr(self):
        # A reference is correctly represented.
        tests = (
            (make_reference(),
             '<Reference: cs:~myuser/precise/juju-gui-42>'),
            (make_reference(schema='local'),
             '<Reference: local:~myuser/precise/juju-gui-42>'),
            (make_reference(user=''),
             '<Reference: cs:precise/juju-gui-42>'),
            (make_reference(user='dalek', revision=None, series='bundle'),
             '<Reference: cs:~dalek/bundle/juju-gui>'),
            (make_reference(name='django', series='vivid', revision=0),
             '<Reference: cs:~myuser/vivid/django-0>'),
            (make_reference(user='', revision=None),
             '<Reference: cs:precise/juju-gui>'),
        )
        for ref, expected_value in tests:
            self.assertEqual(expected_value, repr(ref))

    def test_path(self):
        # The reference path is properly returned as a URL string without the
        # schema.
        tests = (
            (make_reference(),
             '~myuser/precise/juju-gui-42'),
            (make_reference(schema='local'),
             '~myuser/precise/juju-gui-42'),
            (make_reference(user=''),
             'precise/juju-gui-42'),
            (make_reference(user='dalek', revision=None, series='bundle'),
             '~dalek/bundle/juju-gui'),
            (make_reference(name='django', series='vivid', revision=0),
             '~myuser/vivid/django-0'),
            (make_reference(user='', revision=None),
             'precise/juju-gui'),
        )
        for ref, expected_value in tests:
            self.assertEqual(expected_value, ref.path())

    def test_id(self):
        # The reference id is correctly returned.
        tests = (
            (make_reference(),
             'cs:~myuser/precise/juju-gui-42'),
            (make_reference(schema='local'),
             'local:~myuser/precise/juju-gui-42'),
            (make_reference(user=''),
             'cs:precise/juju-gui-42'),
            (make_reference(user='dalek', revision=None, series='bundle'),
             'cs:~dalek/bundle/juju-gui'),
            (make_reference(name='django', series='vivid', revision=0),
             'cs:~myuser/vivid/django-0'),
            (make_reference(user='', revision=None),
             'cs:precise/juju-gui'),
        )
        for ref, expected_value in tests:
            self.assertEqual(expected_value, ref.id())

    def test_jujucharms_id(self):
        # It is possible to return the reference identifier in jujucharms.com.
        tests = (
            (make_reference(),
             'u/myuser/juju-gui/precise/42'),
            (make_reference(schema='local'),
             'u/myuser/juju-gui/precise/42'),
            (make_reference(user=''),
             'juju-gui/precise/42'),
            (make_reference(user='dalek', revision=None, series='bundle'),
             'u/dalek/juju-gui'),
            (make_reference(name='django', series='vivid', revision=0),
             'u/myuser/django/vivid/0'),
            (make_reference(user='', revision=None),
             'juju-gui/precise'),
            (make_reference(user='', series='bundle', revision=None),
             'juju-gui'),
        )
        for ref, expected_value in tests:
            self.assertEqual(expected_value, ref.jujucharms_id())

    def test_jujucharms_url(self):
        # The corresponding charm or bundle page in jujucharms.com is correctly
        # returned.
        tests = (
            (make_reference(),
             'u/myuser/juju-gui/precise/42'),
            (make_reference(schema='local'),
             'u/myuser/juju-gui/precise/42'),
            (make_reference(user=''),
             'juju-gui/precise/42'),
            (make_reference(user='dalek', revision=None, series='bundle'),
             'u/dalek/juju-gui'),
            (make_reference(name='django', series='vivid', revision=0),
             'u/myuser/django/vivid/0'),
            (make_reference(user='', revision=None),
             'juju-gui/precise'),
            (make_reference(user='', series='bundle', revision=None),
             'juju-gui'),
        )
        for ref, expected_value in tests:
            expected_url = settings.JUJUCHARMS_URL + expected_value
            self.assertEqual(expected_url, ref.jujucharms_url())

    def test_charm_entity(self):
        # The is_bundle method returns False for charm references.
        ref = make_reference(series='vivid')
        self.assertFalse(ref.is_bundle())

    def test_bundle_entity(self):
        # The is_bundle method returns True for bundle references.
        ref = make_reference(series='bundle')
        self.assertTrue(ref.is_bundle())

    def test_charm_store_entity(self):
        # The is_local method returns False for charm store references.
        ref = make_reference(schema='cs')
        self.assertFalse(ref.is_local())

    def test_local_entity(self):
        # The is_local method returns True for local references.
        ref = make_reference(schema='local')
        self.assertTrue(ref.is_local())

    def test_equality(self):
        # Two references are equal if they have the same URL.
        self.assertEqual(make_reference(), make_reference())
        self.assertEqual(make_reference(user=''), make_reference(user=''))
        self.assertEqual(
            make_reference(revision=None), make_reference(revision=None))

    def test_equality_different_references(self):
        # Two references with different attributes are not equal.
        tests = (
            (make_reference(schema='cs'),
             make_reference(schema='local')),
            (make_reference(user=''),
             make_reference(user='who')),
            (make_reference(series='trusty'),
             make_reference(series='vivid')),
            (make_reference(name='django'),
             make_reference(name='rails')),
            (make_reference(revision=0),
             make_reference(revision=1)),
            (make_reference(revision=None),
             make_reference(revision=42)),
        )
        for ref1, ref2 in tests:
            self.assertNotEqual(ref1, ref2)

    def test_equality_different_types(self):
        # A reference never equals a non-reference object.
        self.assertNotEqual(make_reference(), 42)
        self.assertNotEqual(make_reference(), True)
        self.assertNotEqual(make_reference(), 'oranges')

    def test_charmworld_id(self):
        # By default, the reference id in charmworld is set to None.
        # XXX frankban 2015-02-26: remove this test once we get rid of the
        # charmworld id concept.
        ref = make_reference()
        self.assertIsNone(ref.charmworld_id)


class TestReferenceFromFullyQualifiedUrl(
        helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_no_schema_error(self):
        # A ValueError is raised if the URL schema is missing.
        expected_error = 'URL has no schema: precise/juju-gui'
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url('precise/juju-gui')

    def test_invalid_schema_error(self):
        # A ValueError is raised if the URL schema is not valid.
        expected_error = 'URL has invalid schema: http'
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'http:precise/juju-gui')

    def test_invalid_user_form_error(self):
        # A ValueError is raised if the user form is not valid.
        expected_error = 'URL has invalid user name form: jean-luc'
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'cs:jean-luc/precise/juju-gui')

    def test_invalid_user_name_error(self):
        # A ValueError is raised if the user name is not valid.
        expected_error = 'URL has invalid user name: jean:luc'
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'cs:~jean:luc/precise/juju-gui')

    def test_local_user_name_error(self):
        # A ValueError is raised if a user is specified on a local entity.
        expected_error = (
            'local entity URL with user name: '
            'local:~jean-luc/precise/juju-gui')
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'local:~jean-luc/precise/juju-gui')

    def test_invalid_form_error(self):
        # A ValueError is raised if the URL is not valid.
        expected_error = 'URL has invalid form: cs:~user/series/name/what-?'
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'cs:~user/series/name/what-?')

    def test_invalid_series_error(self):
        # A ValueError is raised if the series is not valid.
        expected_error = 'URL has invalid series: boo!'
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'cs:boo!/juju-gui-42')

    def test_no_revision_error(self):
        # A ValueError is raised if the entity revision is missing.
        expected_error = 'URL has no revision: cs:series/name'
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url('cs:series/name')

    def test_invalid_revision_error(self):
        # A ValueError is raised if the charm or bundle revision is not valid.
        expected_error = 'URL has invalid revision: revision'
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'cs:series/name-revision')

    def test_invalid_name_error(self):
        # A ValueError is raised if the entity name is not valid.
        expected_error = 'URL has invalid name: not:valid'
        with self.assert_value_error(expected_error):
            references.Reference.from_fully_qualified_url(
                'cs:precise/not:valid-42')

    def test_success(self):
        # References are correctly instantiated by parsing the fully qualified
        # URL.
        tests = (
            ('cs:~myuser/precise/juju-gui-42',
             make_reference()),
            ('cs:trusty/juju-gui-42',
             make_reference(user='', series='trusty')),
            ('local:precise/juju-gui-42',
             make_reference(schema='local', user='')),
        )
        for url, expected_ref in tests:
            ref = references.Reference.from_fully_qualified_url(url)
            self.assertEqual(expected_ref, ref)


class TestReferenceFromJujucharmsUrl(
        helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_invalid_form(self):
        # A ValueError is raised if the URL is not valid.
        expected_error = 'invalid bundle URL: bad wolf'
        with self.assert_value_error(expected_error):
            references.Reference.from_jujucharms_url('bad wolf')

    def test_success(self):
        # A reference is correctly created from a jujucharms.com identifier or
        # complete URL.
        tests = (
            # Check with both user and revision.
            ('u/myuser/mediawiki/42',
             make_reference(series='bundle', name='mediawiki')),
            ('/u/myuser/mediawiki/42',
             make_reference(series='bundle', name='mediawiki')),
            ('u/myuser/django-scalable/42/',
             make_reference(series='bundle', name='django-scalable')),
            ('{}u/myuser/mediawiki/42'.format(settings.JUJUCHARMS_URL),
             make_reference(series='bundle', name='mediawiki')),
            ('{}u/myuser/mediawiki/42/'.format(settings.JUJUCHARMS_URL),
             make_reference(series='bundle', name='mediawiki')),

            # Check without revision.
            ('u/myuser/mediawiki',
             make_reference(series='bundle', name='mediawiki', revision=None)),
            ('/u/myuser/wordpress',
             make_reference(series='bundle', name='wordpress', revision=None)),
            ('u/myuser/mediawiki/',
             make_reference(series='bundle', name='mediawiki', revision=None)),
            ('{}u/myuser/django'.format(settings.JUJUCHARMS_URL),
             make_reference(series='bundle', name='django', revision=None)),
            ('{}u/myuser/mediawiki/'.format(settings.JUJUCHARMS_URL),
             make_reference(series='bundle', name='mediawiki', revision=None)),

            # Check without the user.
            ('rails-single/42',
             make_reference(user='', series='bundle', name='rails-single')),
            ('/mediawiki/42',
             make_reference(user='', series='bundle', name='mediawiki')),
            ('rails-scalable/42/',
             make_reference(user='', series='bundle', name='rails-scalable')),
            ('{}mediawiki/42'.format(settings.JUJUCHARMS_URL),
             make_reference(user='', series='bundle', name='mediawiki')),
            ('{}django/42/'.format(settings.JUJUCHARMS_URL),
             make_reference(user='', series='bundle', name='django')),

            # Check without user and revision.
            ('mediawiki',
             make_reference(user='', series='bundle', name='mediawiki',
                            revision=None)),
            ('/wordpress',
             make_reference(user='', series='bundle', name='wordpress',
                            revision=None)),
            ('mediawiki/',
             make_reference(user='', series='bundle', name='mediawiki',
                            revision=None)),
            ('{}django'.format(settings.JUJUCHARMS_URL),
             make_reference(user='', series='bundle', name='django',
                            revision=None)),
            ('{}mediawiki/'.format(settings.JUJUCHARMS_URL),
             make_reference(user='', series='bundle', name='mediawiki',
                            revision=None)),

            # Check charm entities.
            ('mediawiki/trusty/0',
             make_reference(user='', series='trusty', name='mediawiki',
                            revision=0)),
            ('/wordpress/precise',
             make_reference(user='', series='precise', name='wordpress',
                            revision=None)),
            ('u/who/rails/vivid',
             make_reference(user='who', series='vivid', name='rails',
                            revision=None)),
        )
        for url, expected_ref in tests:
            ref = references.Reference.from_jujucharms_url(url)
            self.assertEqual(expected_ref, ref)
