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

"""Tests for the Juju Quickstart bundles management."""

from __future__ import unicode_literals

import json
import unittest

import mock
import yaml

from quickstart import (
    netutils,
    settings,
)
from quickstart.models import (
    bundles,
    references,
)
from quickstart.tests import helpers


class TestBundle(helpers.BundleFileTestsMixin, unittest.TestCase):

    reference = references.Reference.from_jujucharms_url('django')

    def setUp(self):
        # Create a bundle instance.
        self.bundle = bundles.Bundle(
            self.bundle_data, reference=self.reference)

    def test_attributes(self):
        # The bundle data and the optional reference are stored as attributes.
        self.assertEqual(self.bundle_data, self.bundle.data)
        self.assertEqual(self.reference, self.bundle.reference)

    def test_string(self):
        # The bundle correctly represents itself as a string.
        self.assertEqual('bundle django', str(self.bundle))
        # Create a bundle without a reference.
        bundle = bundles.Bundle(self.bundle_data)
        self.assertEqual('bundle', str(bundle))

    def test_repr(self):
        # The bundle correctly represents itself as an object.
        self.assertEqual('<Bundle: bundle django>', repr(self.bundle))
        # Create a bundle without a reference.
        bundle = bundles.Bundle(self.bundle_data)
        self.assertEqual('<Bundle: bundle>', repr(bundle))

    def test_serialization(self):
        # The bundle data is correctly serialized into a YAML encoded string.
        content = self.bundle.serialize()
        self.assertEqual('services:\n  mysql: {}\n  wordpress: {}\n', content)

    def test_legacy_serialization(self):
        # The bundle data can be serialized for legacy API version 3.
        content = self.bundle.serialize_legacy()
        self.assertEqual(
            'bundle:\n  services:\n    mysql: {}\n    wordpress: {}\n',
            content)

    def test_services(self):
        # Bundle services can be easily retrieved.
        self.assertEqual(['mysql', 'wordpress'], self.bundle.services())


class TestFromSource(
        helpers.BundleFileTestsMixin, helpers.UrlReadTestsMixin,
        helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_charmworld_bundle(self):
        # A bundle instance is properly returned from a charmworld id source.
        with self.patch_urlread(contents=self.bundle_content) as mock_urlread:
            bundle = bundles.from_source('bundle:mediawiki/single')
        self.assertEqual(self.bundle_data, bundle.data)
        self.assertEqual('cs:bundle/mediawiki-single', bundle.reference.id())
        # The charmworld id is properly set when passing charmworld URLs.
        # XXX frankban 2015-03-09: remove this check once we get rid of the
        # charmworld id concept.
        self.assertEqual('mediawiki/single', bundle.reference.charmworld_id)
        mock_urlread.assert_called_once_with(
            settings.CHARMSTORE_API +
            'bundle/mediawiki-single/archive/bundle.yaml')

    def test_charmworld_bundle_with_user_and_revision(self):
        # A specific revision of a user owned bundle is properly returned from
        # a charmworld id source.
        with self.patch_urlread(contents=self.bundle_content) as mock_urlread:
            bundle = bundles.from_source('bundle:~who/mediawiki/42/single')
        self.assertEqual(self.bundle_data, bundle.data)
        self.assertEqual(
            'cs:~who/bundle/mediawiki-single-42', bundle.reference.id())
        # The charmworld id is properly set when passing charmworld URLs.
        # XXX frankban 2015-03-09: remove this check once we get rid of the
        # charmworld id concept.
        self.assertEqual(
            '~who/mediawiki/42/single', bundle.reference.charmworld_id)
        mock_urlread.assert_called_once_with(
            settings.CHARMSTORE_API +
            '~who/bundle/mediawiki-single-42/archive/bundle.yaml')

    def test_charmworld_bundle_from_legacy(self):
        # A bundle instance is properly returned from a charmworld id source
        # by looking at the legacy YAML stored in the charm store.
        side_effect = [
            # A first call urlread returns a not found error.
            netutils.NotFoundError('boo!'),
            # A second call to retrieve the legacy data succeeds.
            self.legacy_bundle_content,
            # The third call to retrieve the new data succeeds.
            self.bundle_content,
        ]
        with self.patch_urlread(error=side_effect) as mock_urlread:
            bundle = bundles.from_source('bundle:mediawiki/bundle1')
        self.assertEqual(self.bundle_data, bundle.data)
        self.assertEqual('cs:bundle/mediawiki', bundle.reference.id())
        # The charmworld id is properly set when passing charmworld URLs.
        # XXX frankban 2015-03-09: remove this check once we get rid of the
        # charmworld id concept.
        self.assertEqual('mediawiki/bundle1', bundle.reference.charmworld_id)
        # The urlread function has been called three times: the first time
        # including both the basket and the bundle name, the second time
        # to retrieve the legacy bundle YAML, the third time to retrieve the
        # new bundle YAML (this time without including the basket name).
        self.assertEqual(len(side_effect), mock_urlread.call_count)
        mock_urlread.assert_has_calls([
            mock.call(
                settings.CHARMSTORE_API +
                'bundle/mediawiki-bundle1/archive/bundle.yaml'),
            mock.call(
                settings.CHARMSTORE_API +
                'bundle/mediawiki/archive/bundles.yaml.orig'),
            mock.call(
                settings.CHARMSTORE_API +
                'bundle/mediawiki/archive/bundle.yaml'),
        ])

    def test_charmworld_bundle_deprecation_warning(self):
        # A deprecation warning is printed if the no longer supported
        # charmworld bundle identifiers are used.
        expected_logs = [
            'this bundle URL is deprecated: please use the new format: '
            'mediawiki-single']
        with self.patch_urlread(contents=self.bundle_content):
            with helpers.assert_logs(expected_logs, 'warn'):
                bundles.from_source('bundle:mediawiki/single')

    def test_charmworld_bundle_invalid_url(self):
        # A ValueError is raised if the provided charmworld id is not valid.
        with self.assert_value_error('invalid bundle URL: bundle:invalid'):
            bundles.from_source('bundle:invalid')

    def test_charmworld_bundle_invalid_content(self):
        # A ValueError is raised if the content associated with the given
        # charmworld URL is not valid.
        with self.patch_urlread(contents='exterminate!'):
            with self.assert_value_error('invalid YAML content: exterminate!'):
                bundles.from_source('bundle:mediawiki/single')

    def test_charmworld_bundle_connection_error(self):
        # An IOError is raised if a connection problem is encountered while
        # retrieving the charmworld bundle.
        with self.patch_urlread(error=IOError('bad wolf')):
            with self.assertRaises(IOError) as ctx:
                bundles.from_source('bundle:mediawiki/single')
        expected_error = (
            'cannot communicate with the charm store at '
            '{}bundle/mediawiki-single/archive/bundle.yaml: '
            'bad wolf'.format(settings.CHARMSTORE_API))
        self.assertEqual(expected_error, bytes(ctx.exception))

    def test_charmworld_bundle_not_found_error(self):
        # An IOError is raised if a charmworld bundle is not found.
        error = netutils.NotFoundError('bad wolf')
        with self.patch_urlread(error=error) as mock_urlread:
            with self.assertRaises(IOError) as ctx:
                bundles.from_source('bundle:mediawiki/single')
        expected_error = (
            'charm store resource not found at '
            '{}bundle/mediawiki/archive/bundles.yaml.orig: '
            'bad wolf'.format(settings.CHARMSTORE_API))
        self.assertEqual(expected_error, bytes(ctx.exception))
        # The urlread function has been called two times: the first time
        # including both the basket and the bundle name, the second time
        # to retrieve the legacy bundle yaml, only including the basket.
        self.assertEqual(2, mock_urlread.call_count)
        mock_urlread.assert_has_calls([
            mock.call(
                settings.CHARMSTORE_API +
                'bundle/mediawiki-single/archive/bundle.yaml'),
            mock.call(
                settings.CHARMSTORE_API +
                'bundle/mediawiki/archive/bundles.yaml.orig'),
        ])

    def test_charmworld_bundle_from_legacy_invalid_name(self):
        # A ValueError is raised if the given bundle name is not found in
        # the legacy basket.
        legacy_bundle_content = yaml.safe_dump({'scalable': self.bundle_data})
        side_effect = [
            # A first call urlread returns a not found error.
            netutils.NotFoundError('boo!'),
            # A second call succeeds.
            legacy_bundle_content,
        ]
        expected_error = 'bundle single not found, did you mean scalable?'
        with self.patch_urlread(error=side_effect) as mock_urlread:
            with self.assert_value_error(expected_error):
                bundles.from_source('bundle:django/single')
        # The urlread function has been called two times: the first time
        # including both the basket and the bundle name, the second time
        # to retrieve the legacy bundle yaml, only including the basket.
        self.assertEqual(len(side_effect), mock_urlread.call_count)
        mock_urlread.assert_has_calls([
            mock.call(
                settings.CHARMSTORE_API +
                'bundle/django-single/archive/bundle.yaml'),
            mock.call(
                settings.CHARMSTORE_API +
                'bundle/django/archive/bundles.yaml.orig'),
        ])

    def test_charmworld_bundle_from_legacy_not_found_error(self):
        # An IOError is raised if the legacy bundle cannot be found.
        side_effect = [
            # A first call urlread returns a not found error.
            netutils.NotFoundError('boo!'),
            # A second call to retrieve the legacy bundle data succeeds.
            self.legacy_bundle_content,
            # The third call to get the bundle from the new API endpoint fails.
            # Note that this is unlikely to happen.
            netutils.NotFoundError('what!'),
        ]
        expected_error = (
            'charm store resource not found at '
            '{}bundle/django/archive/bundle.yaml: '
            'what!'.format(settings.CHARMSTORE_API))
        with self.patch_urlread(error=side_effect) as mock_urlread:
            with self.assertRaises(IOError) as ctx:
                bundles.from_source('bundle:django/bundle1')
        self.assertEqual(expected_error, bytes(ctx.exception))
        # The urlread function has been called three times: the first time
        # including both the basket and the bundle name, the second time
        # to retrieve the legacy bundle YAML, the third time to retrieve the
        # new bundle YAML (this time without including the basket name).
        self.assertEqual(len(side_effect), mock_urlread.call_count)
        mock_urlread.assert_has_calls([
            mock.call(
                settings.CHARMSTORE_API +
                'bundle/django-bundle1/archive/bundle.yaml'),
            mock.call(
                settings.CHARMSTORE_API +
                'bundle/django/archive/bundles.yaml.orig'),
            mock.call(
                settings.CHARMSTORE_API +
                'bundle/django/archive/bundle.yaml'),
        ])

    def test_jujucharms_bundle(self):
        # A bundle instance is properly returned from a jujucharms.com id.
        with self.patch_urlread(contents=self.bundle_content) as mock_urlread:
            bundle = bundles.from_source('django')
        self.assertEqual(self.bundle_data, bundle.data)
        self.assertEqual('cs:bundle/django', bundle.reference.id())
        mock_urlread.assert_called_once_with(
            settings.CHARMSTORE_API + 'bundle/django/archive/bundle.yaml')

    def test_jujucharms_bundle_with_user_and_revision(self):
        # A specific revision of a user owned bundle is properly returned from
        # a jujucharms.com id source.
        with self.patch_urlread(contents=self.bundle_content) as mock_urlread:
            bundle = bundles.from_source('u/who/mediawiki-single/42')
        self.assertEqual(self.bundle_data, bundle.data)
        self.assertEqual(
            'cs:~who/bundle/mediawiki-single-42', bundle.reference.id())
        mock_urlread.assert_called_once_with(
            settings.CHARMSTORE_API +
            '~who/bundle/mediawiki-single-42/archive/bundle.yaml')

    def test_jujucharms_bundle_charm_error(self):
        # A ValueError is raised if the given jujucharms.com id refers to a
        # charm and not to a bundle.
        expected_error = 'expected a bundle, provided charm cs:trusty/django'
        with self.assert_value_error(expected_error):
            bundles.from_source('django/trusty')

    def test_jujucharms_bundle_invalid_url(self):
        # A ValueError is raised if the provided jujucharms.com identifier is
        # not valid.
        with self.assert_value_error('invalid bundle URL: u/no/such/bundle/!'):
            bundles.from_source('u/no/such/bundle/!')

    def test_jujucharms_bundle_invalid_content(self):
        # A ValueError is raised if the content associated with the given
        # jujucharms.com URL are not valid.
        with self.patch_urlread(contents='exterminate!'):
            with self.assert_value_error('invalid YAML content: exterminate!'):
                bundles.from_source('wordpress-scalable')

    def test_jujucharms_bundle_connection_error(self):
        # An IOError is raised if a connection problem is encountered while
        # retrieving the jujucharms.com bundle.
        with self.patch_urlread(error=IOError('bad wolf')):
            with self.assertRaises(IOError) as ctx:
                bundles.from_source('django/42')
        expected_error = (
            'cannot communicate with the charm store at '
            '{}bundle/django-42/archive/bundle.yaml: '
            'bad wolf'.format(settings.CHARMSTORE_API))
        self.assertEqual(expected_error, bytes(ctx.exception))

    def test_jujucharms_bundle_not_found_error(self):
        # An IOError is raised if a connection problem is encountered while
        # retrieving the jujucharms.com bundle.
        with self.patch_urlread(error=netutils.NotFoundError('bad wolf')):
            with self.assertRaises(IOError) as ctx:
                bundles.from_source('django/42')
        expected_error = (
            'charm store resource not found at '
            '{}bundle/django-42/archive/bundle.yaml: '
            'bad wolf'.format(settings.CHARMSTORE_API))
        self.assertEqual(expected_error, bytes(ctx.exception))

    def test_local_file(self):
        # A bundle instance can be created from a local file source.
        # In this case, the resulting bundle does not have a reference.
        path = self.make_bundle_file()
        bundle = bundles.from_source(path)
        self.assertEqual(self.bundle_data, bundle.data)
        self.assertIsNone(bundle.reference)

    def test_local_file_legacy_bundle(self):
        # A bundle instance can be created from a local file source including
        # a legacy version 3 bundle.
        # In this case, the resulting bundle does not have a reference.
        legacy_bundle_data = {
            'bundle': {'services': {'wordpress': {}, 'mysql': {}}},
        }
        path = self.make_bundle_file(legacy_bundle_data)
        bundle = bundles.from_source(path)
        self.assertEqual(legacy_bundle_data['bundle'], bundle.data)
        self.assertIsNone(bundle.reference)

    def test_local_file_not_found(self):
        # An IOError is raised if a local file source cannot be found.
        with self.assertRaises(IOError) as ctx:
            bundles.from_source('/no/such/file.yaml')
        expected_error = (
            'cannot retrieve bundle from local file: '
            "[Errno 2] No such file or directory: '/no/such/file.yaml'")
        self.assertEqual(expected_error, bytes(ctx.exception))

    def test_local_file_legacy_bundle_no_bundles_error(self):
        # A ValueError is raised if a local file contains a legacy version 3
        # YAML content with no bundles defined.
        path = self.make_bundle_file({})
        expected_error = 'no bundles found in the provided list of bundles'
        with self.assert_value_error(expected_error):
            bundles.from_source(path)

    def test_local_file_legacy_bundle_multiple_bundles_error(self):
        # A ValueError is raised if a local file contains a legacy version 3
        # YAML content with multiple bundles defined and the bundle name is
        # not provided for disambiguation.
        path = self.make_bundle_file(self.legacy_bundle_content)
        expected_error = (
            'multiple bundles found (bundle1, bundle2) '
            'but no bundle name specified')
        with self.assert_value_error(expected_error):
            bundles.from_source(path)

    def test_local_file_legacy_bundle_multiple_bundles_name_not_found(self):
        # A ValueError is raised if a local file contains a legacy version 3
        # YAML content with multiple bundles defined and the provided bundle
        # name is not included in the list.
        path = self.make_bundle_file(self.legacy_bundle_content)
        expected_error = (
            'bundle mybundle not found in the provided list of bundles '
            '(bundle1, bundle2)')
        with self.assert_value_error(expected_error):
            bundles.from_source(path, 'mybundle')

    def test_local_file_legacy_bundle_single_bundle_name_not_found(self):
        # A ValueError is raised if a local file contains a legacy version 3
        # YAML content with one bundle defined and the provided bundle name
        # does not match.
        path = self.make_bundle_file({'scalable': self.bundle_data})
        expected_error = 'bundle mybundle not found, did you mean scalable?'
        with self.assert_value_error(expected_error):
            bundles.from_source(path, 'mybundle')

    def test_local_file_legacy_bundle_invalid_bundle_content(self):
        # A ValueError is raised if a local file contains an invalid legacy
        # version 3 content.
        path = self.make_bundle_file({'bundle': '42'})
        expected_error = "invalid YAML content: 42"
        with self.assert_value_error(expected_error):
            bundles.from_source(path, 'bundle')

    def test_remote_url(self):
        # A bundle instance can be created from an arbitrary remote URL
        # pointing to a valid YAML/JSON content.
        # In this case, the resulting bundle does not have a reference.
        with self.patch_urlread(contents=self.bundle_content) as mock_urlread:
            bundle = bundles.from_source('https://1.2.3.4')
        self.assertEqual(self.bundle_data, bundle.data)
        self.assertIsNone(bundle.reference)
        mock_urlread.assert_called_once_with('https://1.2.3.4')

    def test_remote_url_legacy_bundle(self):
        # A bundle instance can be created from an arbitrary remote URL
        # pointing to a legacy version 3 content.
        # In this case, the resulting bundle does not have a reference.
        content = self.legacy_bundle_content
        with self.patch_urlread(contents=content) as mock_urlread:
            bundle = bundles.from_source('https://1.2.3.4:8000', 'bundle2')
        self.assertEqual(self.legacy_bundle_data['bundle2'], bundle.data)
        self.assertIsNone(bundle.reference)
        mock_urlread.assert_called_once_with('https://1.2.3.4:8000')

    def test_remote_url_not_reachable(self):
        # An IOError is raised if a network problem is encountered while
        # trying to reach the remote URL.
        with self.patch_urlread(error=IOError('bad wolf')):
            with self.assertRaises(IOError) as ctx:
                bundles.from_source('https://1.2.3.4')
        expected_error = (
            'cannot retrieve bundle from remote URL https://1.2.3.4: bad wolf')
        self.assertEqual(expected_error, bytes(ctx.exception))

    def test_remote_url_legacy_bundle_no_bundles_error(self):
        # A ValueError is raised if a remote URL contains a legacy version 3
        # YAML content with no bundles defined.
        expected_error = 'no bundles found in the provided list of bundles'
        with self.patch_urlread(contents='{}'):
            with self.assert_value_error(expected_error):
                bundles.from_source('http://1.2.3.4')

    def test_remote_url_legacy_bundle_multiple_bundles_error(self):
        # A ValueError is raised if a remote URL contains a legacy version 3
        # YAML content with multiple bundles defined and the bundle name is
        # not provided for disambiguation.
        expected_error = (
            'multiple bundles found (bundle1, bundle2) '
            'but no bundle name specified')
        with self.patch_urlread(contents=self.legacy_bundle_content):
            with self.assert_value_error(expected_error):
                bundles.from_source('http://1.2.3.4')

    def test_remote_url_legacy_bundle_multiple_bundles_name_not_found(self):
        # A ValueError is raised if a remote URL contains a legacy version 3
        # YAML content with multiple bundles defined and the provided bundle
        # name is not included in the list.
        expected_error = (
            'bundle no-such not found in the provided list of bundles '
            '(bundle1, bundle2)')
        with self.patch_urlread(contents=self.legacy_bundle_content):
            with self.assert_value_error(expected_error):
                bundles.from_source('http://1.2.3.4', 'no-such')

    def test_remote_url_legacy_bundle_single_bundle_name_not_found(self):
        # A ValueError is raised if a remote URL contains a legacy version 3
        # YAML content with one bundle defined and the provided bundle name
        # does not match.
        legacy_bundle_content = yaml.safe_dump({'scalable': self.bundle_data})
        expected_error = 'bundle no-such not found, did you mean scalable?'
        with self.patch_urlread(contents=legacy_bundle_content):
            with self.assert_value_error(expected_error):
                bundles.from_source('http://1.2.3.4', 'no-such')

    def test_remote_url_legacy_bundle_invalid_bundle_content(self):
        # A ValueError is raised if a remote URL contains an invalid legacy
        # version 3 content.
        with self.patch_urlread(contents='bad wolf'):
            with self.assert_value_error('invalid YAML content: bad wolf'):
                bundles.from_source('http://1.2.3.4', 'bundle')


class TestParseYAML(
        helpers.BundleFileTestsMixin, helpers.ValueErrorTestsMixin,
        unittest.TestCase):

    def test_invalid_yaml(self):
        # A ValueError is raised if the bundle content is not a valid YAML.
        with self.assertRaises(ValueError) as ctx:
            bundles.parse_yaml(':')
        expected = 'unable to parse the bundle'
        self.assertIn(expected, bytes(ctx.exception))

    def test_yaml_invalid_type(self):
        # A ValueError is raised if the bundle content is not well formed.
        with self.assert_value_error('invalid YAML content: a-string'):
            bundles.parse_yaml('a-string')

    def test_yaml_invalid_bundle_data(self):
        # A ValueError is raised if the bundle content is not well formed.
        contents = yaml.safe_dump('not valid')
        with self.assert_value_error('invalid YAML content: not valid'):
            bundles.parse_yaml(contents)

    def test_yaml_no_services(self):
        # A ValueError is raised if the bundle does not include services.
        contents = yaml.safe_dump({})
        with self.assert_value_error('unable to retrieve bundle services: {}'):
            bundles.parse_yaml(contents)

    def test_yaml_none_bundle_services(self):
        # A ValueError is raised if services are None.
        contents = yaml.safe_dump({'services': None})
        expected = 'unable to retrieve bundle services: services: null'
        with self.assert_value_error(expected):
            bundles.parse_yaml(contents)

    def test_yaml_invalid_bundle_services_type(self):
        # A ValueError is raised if services have an invalid type.
        contents = yaml.safe_dump({'services': 42})
        expected = 'unable to retrieve bundle services: services: 42'
        with self.assert_value_error(expected):
            bundles.parse_yaml(contents)

    def test_no_services(self):
        # A ValueError is raised if the specified bundle does not contain
        # services.
        contents = yaml.safe_dump({'services': {}})
        with self.assert_value_error('no services found in the bundle'):
            bundles.parse_yaml(contents)

    def test_yaml_gui_in_services(self):
        # A ValueError is raised if the bundle contains juju-gui.
        contents = yaml.safe_dump({
            'services': {settings.JUJU_GUI_SERVICE_NAME: {}},
        })
        expected_error = (
            'the provided bundle contains an instance of juju-gui. Juju '
            'Quickstart will install the latest version of the Juju GUI '
            'automatically; please remove juju-gui from the bundle')
        with self.assert_value_error(expected_error):
            bundles.parse_yaml(contents)

    def test_success(self):
        # The function succeeds when a valid bundle content is provided.
        data = bundles.parse_yaml(self.bundle_content)
        self.assertEqual(self.bundle_data, data)

    def test_success_json(self):
        # Since JSON is a subset of YAML, the function also support JSON
        # encoded bundles.
        content = json.dumps(self.bundle_data)
        data = bundles.parse_yaml(content)
        self.assertEqual(self.bundle_data, data)


class TestIsLegacyBundle(helpers.BundleFileTestsMixin, unittest.TestCase):

    def test_v4_bundle(self):
        # False is returned for new-style version 4 bundles.
        self.assertFalse(bundles.is_legacy_bundle(self.bundle_data))

    def test_legacy_bundle(self):
        # True is returned for legacy bundles.
        tests = (
            self.legacy_bundle_data,
            {'services': {'services': {}}},
        )
        for data in tests:
            self.assertTrue(bundles.is_legacy_bundle(data))


class TestValidate(
        helpers.BundleFileTestsMixin, helpers.ValueErrorTestsMixin,
        unittest.TestCase):

    def test_yaml_no_services(self):
        # A ValueError is raised if the bundle does not include services.
        with self.assert_value_error('unable to retrieve bundle services: {}'):
            bundles.validate({})

    def test_yaml_none_bundle_services(self):
        # A ValueError is raised if services are None.
        expected = 'unable to retrieve bundle services: services: null'
        with self.assert_value_error(expected):
            bundles.validate({'services': None})

    def test_yaml_invalid_bundle_services_type(self):
        # A ValueError is raised if services have an invalid type.
        expected = 'unable to retrieve bundle services: services: 42'
        with self.assert_value_error(expected):
            bundles.validate({'services': 42})

    def test_no_services(self):
        # A ValueError is raised if the specified bundle does not contain
        # services.
        with self.assert_value_error('no services found in the bundle'):
            bundles.validate({'services': {}})

    def test_yaml_gui_in_services(self):
        # A ValueError is raised if the bundle contains juju-gui.
        expected_error = (
            'the provided bundle contains an instance of juju-gui. Juju '
            'Quickstart will install the latest version of the Juju GUI '
            'automatically; please remove juju-gui from the bundle')
        with self.assert_value_error(expected_error):
            bundles.validate({
                'services': {settings.JUJU_GUI_SERVICE_NAME: {}},
            })

    def test_success(self):
        # The function succeeds when a valid bundle content is provided.
        bundles.validate(self.bundle_data)
