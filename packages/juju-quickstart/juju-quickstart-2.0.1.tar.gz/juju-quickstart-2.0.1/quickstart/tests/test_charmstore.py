# This file is part of the Juju Quickstart Plugin, which lets users set up a
# Juju environment in very few steps (https://launchpad.net/juju-quickstart).
# Copyright (C) 2015 Canonical Ltd.
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

"""Tests for the Juju Quickstart charm store communication utilities."""

from __future__ import unicode_literals

import unittest

import json

from quickstart import (
    charmstore,
    netutils,
    settings,
)
from quickstart.models import references
from quickstart.tests import helpers


class TestNotFoundError(unittest.TestCase):

    def test_error_message(self):
        # The error message can be properly retrieved.
        err = charmstore.NotFoundError(b'bad wolf')
        self.assertEqual('bad wolf', bytes(err))


class TestGet(helpers.UrlReadTestsMixin, unittest.TestCase):

    def test_success(self):
        # A GET request to the charm store is correctly performed.
        with self.patch_urlread(contents='ok') as mock_urlread:
            content = charmstore.get('my/path')
        self.assertEqual('ok', content)
        mock_urlread.assert_called_once_with(
            settings.CHARMSTORE_API + 'my/path')

    def test_success_leading_slash(self):
        # The resulting URL is correctly formatted.
        with self.patch_urlread() as mock_urlread:
            charmstore.get('/path/')
        mock_urlread.assert_called_once_with(settings.CHARMSTORE_API + 'path/')

    def test_io_error(self):
        # An IOError is raised if a problem is encountered while connecting to
        # the charm store.
        with self.patch_urlread(error=IOError('bad wolf')):
            with self.assertRaises(IOError) as ctx:
                charmstore.get('/')
        expected_error = (
            'cannot communicate with the charm store at '
            '{}: bad wolf'.format(settings.CHARMSTORE_API))
        self.assertEqual(expected_error, bytes(ctx.exception))

    def test_not_found_error(self):
        # A charmstore.NotFoundError is raised if the request returns a 404 not
        # found response.
        with self.patch_urlread(error=netutils.NotFoundError('bad wolf')):
            with self.assertRaises(charmstore.NotFoundError) as ctx:
                charmstore.get('/no/such')
        expected_error = (
            'charm store resource not found at '
            '{}no/such: bad wolf'.format(settings.CHARMSTORE_API))
        self.assertEqual(expected_error, bytes(ctx.exception))


class TestGetReference(helpers.UrlReadTestsMixin, unittest.TestCase):

    def test_success(self):
        # A GET request to the charm store is correctly performed using the
        # given charm or bundle reference.
        ref = references.Reference.from_jujucharms_url('mediawiki-single')
        with self.patch_urlread(contents='hash') as mock_urlread:
            content = charmstore.get_reference(ref, '/meta/hash')
        self.assertEqual('hash', content)
        mock_urlread.assert_called_once_with(
            settings.CHARMSTORE_API + 'bundle/mediawiki-single/meta/hash')

    def test_success_without_leading_slash(self):
        # The resulting URL is correctly formatted when the static path does
        # not include a leading slash.
        ref = references.Reference.from_jujucharms_url('django/trusty/42')
        with self.patch_urlread() as mock_urlread:
            charmstore.get_reference(ref, 'expand-id')
        mock_urlread.assert_called_once_with(
            settings.CHARMSTORE_API + 'trusty/django-42/expand-id')

    def test_io_error(self):
        # An IOError is raised if a problem is encountered while connecting to
        # the charm store.
        ref = references.Reference.from_jujucharms_url('django/trusty')
        with self.patch_urlread(error=IOError('bad wolf')):
            with self.assertRaises(IOError) as ctx:
                charmstore.get_reference(ref, 'meta/id')
        expected_error = (
            'cannot communicate with the charm store at '
            '{}trusty/django/meta/id: '
            'bad wolf'.format(settings.CHARMSTORE_API))
        self.assertEqual(expected_error, bytes(ctx.exception))

    def test_not_found_error(self):
        # A charmstore.NotFoundError is raised if the reference is not found
        # in the charm store.
        ref = references.Reference.from_jujucharms_url('django')
        with self.patch_urlread(error=netutils.NotFoundError('bad wolf')):
            with self.assertRaises(charmstore.NotFoundError) as ctx:
                charmstore.get_reference(ref, '/no/such')
        expected_error = (
            'charm store resource not found at '
            '{}bundle/django/no/such: '
            'bad wolf'.format(settings.CHARMSTORE_API))
        self.assertEqual(expected_error, bytes(ctx.exception))


class TestResolve(helpers.UrlReadTestsMixin, unittest.TestCase):

    contents = json.dumps({
        'Id': 'cs:trusty/juju-gui-42',
        'Series': 'trusty',
        'Name': 'juju-gui',
        'Revision': 42,
    })

    def test_resolved(self):
        # The resolved entity id is correctly returned.
        with self.patch_urlread(contents=self.contents) as mock_urlread:
            entity_id = charmstore.resolve('juju-gui')
        self.assertEqual('cs:trusty/juju-gui-42', entity_id)
        mock_urlread.assert_called_once_with(
            settings.CHARMSTORE_API + 'juju-gui/meta/id')

    def test_resolved_with_series(self):
        # The resolved entity id is correctly returned when the entity series
        # is specified.
        with self.patch_urlread(contents=self.contents) as mock_urlread:
            entity_id = charmstore.resolve('django', series='vivid')
        self.assertEqual('cs:trusty/juju-gui-42', entity_id)
        mock_urlread.assert_called_once_with(
            settings.CHARMSTORE_API + 'vivid/django/meta/id')

    def test_io_error(self):
        # IOErrors are properly propagated.
        with self.patch_urlread(error=IOError('bad wolf')):
            with self.assertRaises(IOError) as ctx:
                charmstore.resolve('django')
        expected_error = (
            'cannot communicate with the charm store at '
            '{}django/meta/id: bad wolf'.format(settings.CHARMSTORE_API))
        self.assertEqual(expected_error, bytes(ctx.exception))

    def test_not_found_error(self):
        # Not found errors are properly propagated.
        with self.patch_urlread(error=netutils.NotFoundError('bad wolf')):
            with self.assertRaises(charmstore.NotFoundError) as ctx:
                charmstore.resolve('django', series='trusty')
        expected_error = (
            'charm store resource not found at '
            '{}trusty/django/meta/id: '
            'bad wolf'.format(settings.CHARMSTORE_API))
        self.assertEqual(expected_error, bytes(ctx.exception))

    def test_value_error(self):
        # A ValueError is raised if the API response is not valid.
        contents = json.dumps({'invalid': {}})
        with self.patch_urlread(contents=contents):
            with self.assertRaises(ValueError) as ctx:
                charmstore.resolve('juju-gui', series='trusty')
        self.assertEqual(
            'unable to resolve entity id trusty/juju-gui',
            bytes(ctx.exception))


class TestGetBundleData(
        helpers.BundleFileTestsMixin, helpers.UrlReadTestsMixin,
        unittest.TestCase):

    def test_data_retrieved(self):
        # The bundle data is correctly retrieved and parsed.
        ref = references.Reference.from_jujucharms_url('django/42')
        with self.patch_urlread(contents=self.bundle_content) as mock_urlread:
            data = charmstore.get_bundle_data(ref)
        self.assertEqual(self.bundle_data, data)
        mock_urlread.assert_called_once_with(
            settings.CHARMSTORE_API + 'bundle/django-42/archive/bundle.yaml')

    def test_io_error(self):
        # IOErrors are properly propagated.
        ref = references.Reference.from_jujucharms_url('mediawiki-single')
        with self.patch_urlread(error=IOError('bad wolf')):
            with self.assertRaises(IOError) as ctx:
                charmstore.get_bundle_data(ref)
        expected_error = (
            'cannot communicate with the charm store at '
            '{}bundle/mediawiki-single/archive/bundle.yaml: '
            'bad wolf'.format(settings.CHARMSTORE_API))
        self.assertEqual(expected_error, bytes(ctx.exception))

    def test_not_found_error(self):
        # Not found errors are properly propagated.
        ref = references.Reference.from_jujucharms_url('no-such')
        with self.patch_urlread(error=netutils.NotFoundError('bad wolf')):
            with self.assertRaises(charmstore.NotFoundError) as ctx:
                charmstore.get_bundle_data(ref)
        expected_error = (
            'charm store resource not found at '
            '{}bundle/no-such/archive/bundle.yaml: '
            'bad wolf'.format(settings.CHARMSTORE_API))
        self.assertEqual(expected_error, bytes(ctx.exception))

    def test_value_error_invalid_data(self):
        # A ValueError is raised if the API response is not valid.
        ref = references.Reference.from_jujucharms_url('u/who/django')
        with self.patch_urlread(contents='invalid: data:'):
            with self.assertRaises(ValueError) as ctx:
                charmstore.get_bundle_data(ref)
        self.assertIn(
            'unable to parse the bundle content', bytes(ctx.exception))

    def test_value_error_not_a_bundle(self):
        # A ValueError is raised if the API response is not valid.
        ref = references.Reference.from_jujucharms_url('django/trusty/47')
        with self.assertRaises(ValueError) as ctx:
            charmstore.get_bundle_data(ref)
        self.assertEqual(
            'expected a bundle, provided charm cs:trusty/django-47',
            bytes(ctx.exception))


class TestGetLegacyBundleData(
        helpers.BundleFileTestsMixin, helpers.UrlReadTestsMixin,
        unittest.TestCase):

    def test_data_retrieved(self):
        # The legacy bundle data is correctly retrieved and parsed.
        ref = references.Reference.from_jujucharms_url('u/who/django/42')
        contents = self.legacy_bundle_content
        with self.patch_urlread(contents=contents) as mock_urlread:
            data = charmstore.get_legacy_bundle_data(ref)
        self.assertEqual(self.legacy_bundle_data, data)
        mock_urlread.assert_called_once_with(
            settings.CHARMSTORE_API +
            '~who/bundle/django-42/archive/bundles.yaml.orig')

    def test_io_error(self):
        # IOErrors are properly propagated.
        ref = references.Reference.from_jujucharms_url('mediawiki-single')
        with self.patch_urlread(error=IOError('bad wolf')):
            with self.assertRaises(IOError) as ctx:
                charmstore.get_legacy_bundle_data(ref)
        expected_error = (
            'cannot communicate with the charm store at '
            '{}bundle/mediawiki-single/archive/bundles.yaml.orig: '
            'bad wolf'.format(settings.CHARMSTORE_API))
        self.assertEqual(expected_error, bytes(ctx.exception))

    def test_not_found_error(self):
        # Not found errors are properly propagated.
        ref = references.Reference.from_jujucharms_url('no-such')
        with self.patch_urlread(error=netutils.NotFoundError('bad wolf')):
            with self.assertRaises(charmstore.NotFoundError) as ctx:
                charmstore.get_legacy_bundle_data(ref)
        expected_error = (
            'charm store resource not found at '
            '{}bundle/no-such/archive/bundles.yaml.orig: '
            'bad wolf'.format(settings.CHARMSTORE_API))
        self.assertEqual(expected_error, bytes(ctx.exception))

    def test_value_error_invalid_data(self):
        # A ValueError is raised if the API response is not valid.
        ref = references.Reference.from_jujucharms_url('u/who/django')
        with self.patch_urlread(contents='invalid: data:'):
            with self.assertRaises(ValueError) as ctx:
                charmstore.get_legacy_bundle_data(ref)
        self.assertIn(
            'unable to parse the bundle content', bytes(ctx.exception))

    def test_value_error_not_a_bundle(self):
        # A ValueError is raised if the API response is not valid.
        ref = references.Reference.from_jujucharms_url('django/trusty/47')
        with self.assertRaises(ValueError) as ctx:
            charmstore.get_legacy_bundle_data(ref)
        self.assertEqual(
            'expected a bundle, provided charm cs:trusty/django-47',
            bytes(ctx.exception))


class TestLoadBundleYaml(helpers.BundleFileTestsMixin, unittest.TestCase):

    def test_valid_bundle_content(self):
        # The bundle content is correctly loaded.
        data = charmstore.load_bundle_yaml(self.bundle_content)
        self.assertEqual(self.bundle_data, data)

    def test_invalid_bundle_content(self):
        # A ValueError is raised if the bundle content is not valid.
        with self.assertRaises(ValueError) as ctx:
            charmstore.load_bundle_yaml('invalid: content:')
        self.assertIn(
            'unable to parse the bundle content', bytes(ctx.exception))
