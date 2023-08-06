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

"""Tests for the Quickstart Juju utilities and helpers."""

from __future__ import unicode_literals

import unittest

import mock
import yaml

from quickstart import jujutools
from quickstart.models import references
from quickstart.tests import helpers


class TestGetApiUrl(unittest.TestCase):

    def test_new_url(self):
        # The new Juju API endpoint is returned if a recent Juju is used.
        url = jujutools.get_api_url('1.2.3.4:17070', (1, 22, 0), 'env-uuid')
        self.assertEqual('wss://1.2.3.4:17070/environment/env-uuid/api', url)

    def test_new_url_with_prefix(self):
        # The new Juju API endpoint is returned with the given path prefix.
        url = jujutools.get_api_url(
            '1.2.3.4:17070', (1, 22, 0), 'env-uuid', prefix='/my/path/')
        self.assertEqual(
            'wss://1.2.3.4:17070/my/path/environment/env-uuid/api', url)

    def test_old_juju(self):
        # The old Juju API endpoint is returned if the Juju in use is not a
        # recent version.
        url = jujutools.get_api_url('1.2.3.4:17070', (1, 21, 7), 'env-uuid')
        self.assertEqual('wss://1.2.3.4:17070', url)

    def test_old_juju_with_prefix(self):
        # The old Juju API endpoint is returned with the given path prefix.
        url = jujutools.get_api_url(
            '1.2.3.4:8888', (1, 21, 7), 'env-uuid', 'proxy/')
        self.assertEqual('wss://1.2.3.4:8888/proxy', url)

    def test_no_env_uuid(self):
        # The old Juju API endpoint is returned if the environment unique
        # identifier is unreachable.
        url = jujutools.get_api_url('1.2.3.4:17070', (1, 23, 42), None)
        self.assertEqual('wss://1.2.3.4:17070', url)

    def test_no_env_uuid_with_prefix(self):
        # The old Juju API endpoint is returned with the given path prefix.
        url = jujutools.get_api_url(
            '1.2.3.4:17070', (1, 23, 42), None, 'my/prefix')
        self.assertEqual('wss://1.2.3.4:17070/my/prefix', url)

    def test_new_charm_old_juju(self):
        # The old Juju API endpoints are used if and old version of Juju is in
        # use, even if the Juju GUI charm is recent.
        ref = references.Reference.from_fully_qualified_url(
            'cs:trusty/juju-gui-42')
        url = jujutools.get_api_url(
            '1.2.3.4:5678', (1, 21, 7), 'env-uuid', charm_ref=ref)
        self.assertEqual('wss://1.2.3.4:5678', url)

    def test_customized_charm_unexpected_name(self):
        # If a customized Juju GUI charm is used, then we assume it supports
        # the new Juju Login API endpoint (unexpected charm name).
        ref = references.Reference.from_fully_qualified_url(
            'cs:trusty/the-amazing-gui-0')
        url = jujutools.get_api_url(
            'example.com:17070', (1, 22, 2), 'uuid', charm_ref=ref)
        self.assertEqual('wss://example.com:17070/environment/uuid/api', url)

    def test_customized_charm_unexpected_user(self):
        # If a customized Juju GUI charm is used, then we assume it supports
        # the new Juju Login API endpoint (unexpected charm user).
        ref = references.Reference.from_fully_qualified_url(
            'cs:~who/trusty/juju-gui-0')
        url = jujutools.get_api_url(
            'example.com:17070', (1, 22, 2), 'uuid', charm_ref=ref)
        self.assertEqual('wss://example.com:17070/environment/uuid/api', url)

    def test_customized_charm_unexpected_schema(self):
        # If a customized Juju GUI charm is used, then we assume it supports
        # the new Juju Login API endpoint (local charm).
        ref = references.Reference.from_fully_qualified_url(
            'local:precise/juju-gui-0')
        url = jujutools.get_api_url(
            'example.com:17070', (1, 22, 2), 'uuid', prefix='/', charm_ref=ref)
        self.assertEqual('wss://example.com:17070/environment/uuid/api', url)

    def test_customized_charm_unexpected_series(self):
        # If a customized Juju GUI charm is used, then we assume it supports
        # the new Juju Login API endpoint (unsupported charm series).
        ref = references.Reference.from_fully_qualified_url(
            'cs:vivid/juju-gui-0')
        url = jujutools.get_api_url(
            'example.com:22', (1, 22, 2), 'uuid', prefix='ws', charm_ref=ref)
        self.assertEqual('wss://example.com:22/ws/environment/uuid/api', url)

    def test_recent_precise_charm(self):
        # The new API endpoints are used if a recent precise charm is in use.
        ref = references.Reference.from_fully_qualified_url(
            'cs:precise/juju-gui-107')
        url = jujutools.get_api_url(
            '1.2.3.4:4747', (1, 42, 0), 'env-id', charm_ref=ref)
        self.assertEqual('wss://1.2.3.4:4747/environment/env-id/api', url)

    def test_recent_trusty_charm(self):
        # The new API endpoints are used if a recent trusty charm is in use.
        ref = references.Reference.from_fully_qualified_url(
            'cs:trusty/juju-gui-19')
        url = jujutools.get_api_url(
            '1.2.3.4:4747', (1, 42, 0), 'env-id', charm_ref=ref)
        self.assertEqual('wss://1.2.3.4:4747/environment/env-id/api', url)

    def test_old_precise_charm(self):
        # The old API endpoint is returned if the precise Juju GUI charm in use
        # is outdated.
        ref = references.Reference.from_fully_qualified_url(
            'cs:precise/juju-gui-106')
        url = jujutools.get_api_url(
            '1.2.3.4:4747', (1, 42, 0), 'env-uuid', charm_ref=ref)
        self.assertEqual('wss://1.2.3.4:4747', url)

    def test_old_trusty_charm(self):
        # The old API endpoint is returned if the trusty Juju GUI charm in use
        # is outdated.
        ref = references.Reference.from_fully_qualified_url(
            'cs:trusty/juju-gui-18')
        url = jujutools.get_api_url(
            '1.2.3.4:4747', (1, 42, 0), 'env-uuid', prefix='ws', charm_ref=ref)
        self.assertEqual('wss://1.2.3.4:4747/ws', url)

    def test_recent_charm_and_prefix(self):
        # The new API endpoint is returned if a recent charm and a prefix are
        # both provided. This test exercises the real case in which the GUI
        # server API endpoint is returned.
        ref = references.Reference.from_fully_qualified_url(
            'cs:trusty/juju-gui-42')
        url = jujutools.get_api_url(
            '1.2.3.4:17070', (1, 22, 0), 'env-id', prefix='ws', charm_ref=ref)
        self.assertEqual('wss://1.2.3.4:17070/ws/environment/env-id/api', url)


class TestGetServiceInfo(helpers.WatcherDataTestsMixin, unittest.TestCase):

    def test_service_and_unit(self):
        # The data about the given service and unit is correctly returned.
        service_change = self.make_service_change()
        unit_change = self.make_unit_change()
        status = [service_change, unit_change]
        expected = (service_change[2], unit_change[2])
        self.assertEqual(
            expected, jujutools.get_service_info(status, 'my-gui'))

    def test_service_only(self):
        # The data about the given service without units is correctly returned.
        service_change = self.make_service_change()
        status = [service_change]
        expected = (service_change[2], None)
        self.assertEqual(
            expected, jujutools.get_service_info(status, 'my-gui'))

    def test_service_removed(self):
        # A tuple (None, None) is returned if the service is being removed.
        status = [
            self.make_service_change(action='remove'),
            self.make_unit_change(),
        ]
        expected = (None, None)
        self.assertEqual(
            expected, jujutools.get_service_info(status, 'my-gui'))

    def test_another_service(self):
        # A tuple (None, None) is returned if the service is not found.
        status = [
            self.make_service_change(data={'Name': 'another-service'}),
            self.make_unit_change(),
        ]
        expected = (None, None)
        self.assertEqual(
            expected, jujutools.get_service_info(status, 'my-gui'))

    def test_service_not_alive(self):
        # A tuple (None, None) is returned if the service is not alive.
        status = [
            self.make_service_change(data={'Life': 'dying'}),
            self.make_unit_change(),
        ]
        expected = (None, None)
        self.assertEqual(
            expected, jujutools.get_service_info(status, 'my-gui'))

    def test_unit_removed(self):
        # The unit data is not returned if the unit is being removed.
        service_change = self.make_service_change()
        status = [service_change, self.make_unit_change(action='remove')]
        expected = (service_change[2], None)
        self.assertEqual(
            expected, jujutools.get_service_info(status, 'my-gui'))

    def test_another_unit(self):
        # The unit data is not returned if the unit belongs to another service.
        service_change = self.make_service_change()
        status = [
            service_change,
            self.make_unit_change(data={'Service': 'another-service'}),
        ]
        expected = (service_change[2], None)
        self.assertEqual(
            expected, jujutools.get_service_info(status, 'my-gui'))

    def test_no_services(self):
        # A tuple (None, None) is returned no services are found.
        status = [self.make_unit_change()]
        expected = (None, None)
        self.assertEqual(
            expected, jujutools.get_service_info(status, 'my-gui'))

    def test_no_entities(self):
        # A tuple (None, None) is returned no entities are found.
        expected = (None, None)
        self.assertEqual(expected, jujutools.get_service_info([], 'my-gui'))


@mock.patch('__builtin__.print', mock.Mock())
class TestParseGuiCharmUrl(unittest.TestCase):

    def test_charm_instance_returned(self):
        # A charm reference instance is correctly returned.
        ref = jujutools.parse_gui_charm_url('cs:trusty/juju-gui-42')
        self.assertIsInstance(ref, references.Reference)
        self.assertEqual('cs:trusty/juju-gui-42', ref.id())

    def test_customized(self):
        # A customized charm reference is properly logged.
        expected = 'using a customized juju-gui charm'
        with helpers.assert_logs([expected], level='warn'):
            jujutools.parse_gui_charm_url('cs:~juju-gui/precise/juju-gui-28')

    def test_outdated(self):
        # An outdated charm reference is properly logged.
        expected = 'charm is outdated and may not support bundle deployments'
        with helpers.assert_logs([expected], level='warn'):
            jujutools.parse_gui_charm_url('cs:precise/juju-gui-1')

    def test_unexpected(self):
        # An unexpected charm reference is properly logged.
        expected = (
            'unexpected URL for the juju-gui charm: the service may not work '
            'as expected')
        with helpers.assert_logs([expected], level='warn'):
            jujutools.parse_gui_charm_url('cs:precise/another-gui-42')

    def test_official(self):
        # No warnings are logged if an up to date charm is passed.
        with mock.patch('logging.warn') as mock_warn:
            jujutools.parse_gui_charm_url('cs:precise/juju-gui-100')
        self.assertFalse(mock_warn.called)


class TestParseStatusOutput(helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_invalid_yaml(self):
        # A ValueError is raised if the output is not a valid YAML.
        with self.assertRaises(ValueError) as context_manager:
            jujutools.parse_status_output(':')
        expected = 'unable to parse the output'
        self.assertIn(expected, bytes(context_manager.exception))

    def test_invalid_yaml_contents(self):
        # A ValueError is raised if the output is not well formed.
        with self.assert_value_error('invalid YAML contents: a-string'):
            jujutools.parse_status_output('a-string')

    def test_no_agent_state(self):
        # A ValueError is raised if the agent-state is not found in the YAML.
        data = {
            'machines': {
                '0': {'agent-version': '1.17.0.1'},
            },
        }
        expected = 'machines:0:agent-state not found in {}'.format(bytes(data))
        with self.assert_value_error(expected):
            jujutools.get_agent_state(yaml.safe_dump(data))

    def test_success_agent_state(self):
        # The agent state is correctly returned.
        output = yaml.safe_dump({
            'machines': {
                '0': {'agent-version': '1.17.0.1', 'agent-state': 'started'},
            },
        })
        agent_state = jujutools.get_agent_state(output)
        self.assertEqual('started', agent_state)

    def test_no_bootstrap_node_series(self):
        # A ValueError is raised if the series is not found in the YAML.
        data = {
            'machines': {
                '0': {'agent-version': '1.17.0.1'},
            },
        }
        expected = 'machines:0:series not found in {}'.format(bytes(data))
        with self.assert_value_error(expected):
            jujutools.get_bootstrap_node_series(yaml.safe_dump(data))

    def test_success_bootstrap_node_series(self):
        # The bootstrap node series is correctly returned.
        output = yaml.safe_dump({
            'machines': {
                '0': {'agent-version': '1.17.0.1',
                      'agent-state': 'started',
                      'series': 'zydeco'},
            },
        })
        bsn_series = jujutools.get_bootstrap_node_series(output)
        self.assertEqual('zydeco', bsn_series)
