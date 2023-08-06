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

"""Tests for the Juju Quickstart environments watching utilities."""

from __future__ import unicode_literals

import unittest

import mock

from quickstart import watchers
from quickstart.tests import helpers


# Define addresses to be used in tests.
cloud_addresses = [
    {'NetworkName': '',
     'Scope': 'public',
     'Type': 'hostname',
     'Value': 'eu-west-1.compute.example.com'},
    {'NetworkName': '',
     'Scope': 'local-cloud',
     'Type': 'hostname',
     'Value': 'eu-west-1.example.internal'},
    {'NetworkName': '',
     'Scope': 'public',
     'Type': 'ipv4',
     'Value': '444.222.444.222'},
    {'NetworkName': '',
     'Scope': 'local-cloud',
     'Type': 'ipv4',
     'Value': '10.42.47.10'},
    {'NetworkName': '',
     'Scope': '',
     'Type': 'ipv6',
     'Value': 'fe80::92b8:d0ff:fe94:8f8c'},
]
container_addresses = [
    {'NetworkName': '',
     'Scope': '',
     'Type': 'ipv4',
     'Value': '10.0.3.42'},
    {'NetworkName': '',
     'Scope': '',
     'Type': 'ipv6',
     'Value': 'fe80::216:3eff:fefd:787e'},
]


class TestRetrievePublicAddress(unittest.TestCase):

    def resolver(self, hostname):
        """A fake resolver returning no errors."""
        return None

    def test_empty_addresses(self):
        # None is returned if there are no available addresses.
        address = watchers.retrieve_public_adddress([], self.resolver)
        self.assertIsNone(address)

    def test_cloud_address_not_found(self):
        # None is returned if a cloud machine public address is not available.
        addresses = [
            {'NetworkName': '',
             'Scope': 'public',
             'Type': 'ipv6',
             'Value': 'fe80::92b8:d0ff:fe94:8f8c'},
            {'NetworkName': '',
             'Scope': 'local-cloud',
             'Type': 'ipv6',
             'Value': 'fe80::216:3eff:fefd:787e'},
        ]
        address = watchers.retrieve_public_adddress(addresses, self.resolver)
        self.assertIsNone(address)

    def test_container_address_not_found(self):
        # None is returned if an LXC public address is not available.
        addresses = [{
            'NetworkName': '',
            'Scope': '',
            'Type': 'ipv6',
            'Value': 'fe80::216:3eff:fefd:787e',
        }]
        address = watchers.retrieve_public_adddress(addresses, self.resolver)
        self.assertIsNone(address)

    def test_empty_public_address(self):
        # None is returned if the public address has no value.
        addresses = [
            {'NetworkName': '',
             'Scope': 'local-cloud',
             'Type': 'hostname',
             'Value': 'eu-west-1.example.internal'},
            {'NetworkName': '',
             'Scope': 'public',
             'Type': 'ipv4',
             'Value': ''},
        ]
        address = watchers.retrieve_public_adddress(addresses, self.resolver)
        self.assertIsNone(address)

    def test_cloud_addresses(self):
        # The public address of a cloud machine is properly returned.
        address = watchers.retrieve_public_adddress(
            cloud_addresses, self.resolver)
        self.assertEqual('eu-west-1.compute.example.com', address)

    def test_container_addresses(self):
        # The public address of an LXC instance is properly returned.
        address = watchers.retrieve_public_adddress(
            container_addresses, self.resolver)
        self.assertEqual('10.0.3.42', address)

    def test_old_juju_version(self):
        # The public address is properly returned when using Juju < 1.20.
        # Prior to Juju 1.20, the MachineInfo field for the address scope was
        # called "NetworkScope".
        addresses = [
            {'NetworkName': '',
             'NetworkScope': 'public',
             'Type': 'hostname',
             'Value': 'eu-west-1.compute.example.com'},
            {'NetworkName': '',
             'NetworkScope': 'local-cloud',
             'Type': 'hostname',
             'Value': 'eu-west-1.example.internal'},
        ]
        address = watchers.retrieve_public_adddress(addresses, self.resolver)
        self.assertEqual('eu-west-1.compute.example.com', address)

    def test_local_cloud_address(self):
        # If there are no available public addresses the first ipv4 address
        # with cloud-local scope is returned.
        addresses = [
            {'NetworkName': '',
             'Scope': 'local-cloud',
             'Type': 'hostname',
             'Value': 'eu-west-1.example.internal'},
            {'NetworkName': '',
             'Scope': 'local-cloud',
             'Type': 'ipv4',
             'Value': '10.42.47.10'},
            {'NetworkName': '',
             'Scope': 'local-cloud',
             'Type': 'ipv4',
             'Value': '1.2.3.4'},
        ]
        address = watchers.retrieve_public_adddress(addresses, self.resolver)
        self.assertEqual('10.42.47.10', address)

    def test_unknown_address(self):
        # If there are no available public or local-cloud addresses, the first
        # address with unknown scope is returned.
        addresses = [
            {'NetworkName': '',
             'Scope': '',
             'Type': 'ipv4',
             'Value': '10.0.3.42'},
            {'NetworkName': '',
             'Scope': '',
             'Type': 'ipv4',
             'Value': '10.0.3.47'},
        ]
        address = watchers.retrieve_public_adddress(addresses, self.resolver)
        self.assertEqual('10.0.3.42', address)

    def test_preferred_fallback_address(self):
        # If there are no available public addresses the first fallback address
        # in the list is returned.
        addresses = [
            {'NetworkName': '',
             'Scope': '',
             'Type': 'ipv4',
             'Value': '10.0.3.47'},
            {'NetworkName': '',
             'Scope': 'local-cloud',
             'Type': 'ipv4',
             'Value': '10.42.47.10'},

        ]
        address = watchers.retrieve_public_adddress(addresses, self.resolver)
        self.assertEqual('10.0.3.47', address)
        # Now test with a reversed order.
        address = watchers.retrieve_public_adddress(
            reversed(addresses), self.resolver)
        self.assertEqual('10.42.47.10', address)

    def test_unresolvable_public_address(self):
        # None is returned if a public cloud is found but it is not resolvable.
        addresses = [
            {'NetworkName': '',
             'Scope': 'public',
             'Type': 'hostname',
             'Value': 'eu-west-1.example.internal'},
        ]
        expected_warning = (
            'cannot resolve public eu-west-1.example.internal address, '
            'looking for another candidate: bad wolf')
        with helpers.assert_logs([expected_warning], level='warn'):
            address = watchers.retrieve_public_adddress(
                addresses, lambda hostname: 'bad wolf')
        self.assertIsNone(address)

    def test_unresolvable_public_address_fallback(self):
        # If there are no resolvable public addresses the first ipv4 address
        # with cloud-local scope is returned.
        address = watchers.retrieve_public_adddress(
            cloud_addresses, lambda hostname: 'bad wolf')
        self.assertEqual('10.42.47.10', address)


class TestParseMachineChange(helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_machine_removed(self):
        # A ValueError is raised if the change represents a machine removal.
        data = {'Addresses': [], 'Id': '1', 'Status': 'started'}
        with self.assert_value_error('machine 1 unexpectedly removed'):
            watchers.parse_machine_change('remove', data, '', '')

    def test_machine_error(self):
        # A ValueError is raised if the machine is in an error state.
        data = {
            'Addresses': [],
            'Id': '1',
            'Status': 'error',
            'StatusInfo': 'bad wolf',
        }
        expected_error = 'machine 1 is in an error state: error: bad wolf'
        with self.assert_value_error(expected_error):
            watchers.parse_machine_change('change', data, '', '')

    @helpers.mock_print
    def test_pending_status_notified(self, mock_print):
        # A message is printed to stdout when the machine changes its status
        # to "pending". The new status is also returned by the function.
        data = {'Addresses': [], 'Id': '1', 'Status': 'pending'}
        status, address = watchers.parse_machine_change('change', data, '', '')
        self.assertEqual('pending', status)
        self.assertEqual('', address)
        mock_print.assert_called_once_with('machine 1 provisioning is pending')

    @helpers.mock_print
    def test_started_status_notified(self, mock_print):
        # A message is printed to stdout when the machine changes its status
        # to "started". The new status is also returned by the function.
        data = {'Addresses': [], 'Id': '42', 'Status': 'started'}
        status, address = watchers.parse_machine_change(
            'change', data, 'pending', '')
        self.assertEqual('started', status)
        self.assertEqual('', address)
        mock_print.assert_called_once_with('machine 42 is started')

    @helpers.mock_print
    def test_status_not_changed(self, mock_print):
        # If the status in the machine change and the given current status are
        # the same value, nothing is printed and the status is returned.
        data = {'Addresses': [], 'Id': '47', 'Status': 'pending'}
        status, address = watchers.parse_machine_change(
            'change', data, 'pending', '')
        self.assertEqual('pending', status)
        self.assertEqual('', address)
        self.assertFalse(mock_print.called)

    @helpers.mock_print
    def test_address_notified(self, mock_print):
        # A message is printed to stdout when the machine obtains a public
        # address.
        data = {'Addresses': cloud_addresses, 'Id': '1', 'Status': 'pending'}
        # Patch the hostname resolver used to check hostname addresses.
        # Note that resolve error cases are properly exercised by the
        # watchers.retrieve_public_adddress tests.
        with helpers.patch_check_resolvable():
            status, address = watchers.parse_machine_change(
                'change', data, 'pending', '')
        self.assertEqual('pending', status)
        self.assertEqual('eu-west-1.compute.example.com', address)
        mock_print.assert_called_once_with(
            'unit placed on eu-west-1.compute.example.com')

    @helpers.mock_print
    def test_both_status_and_address_notified(self, mock_print):
        # Both status and public address changes are notified if required.
        data = {
            'Addresses': container_addresses,
            'Id': '0',
            'Status': 'started',
        }
        status, address = watchers.parse_machine_change(
            'change', data, 'pending', '')
        self.assertEqual('started', status)
        self.assertEqual('10.0.3.42', address)
        self.assertEqual(2, mock_print.call_count)
        mock_print.assert_has_calls([
            mock.call('unit placed on 10.0.3.42'),
            mock.call('machine 0 is started'),
        ])

    @helpers.mock_print
    def test_address_not_available(self, mock_print):
        # An empty address is returned when the addresses field is not
        # included in the change data.
        data = {'Id': '47', 'Status': 'pending'}
        status, address = watchers.parse_machine_change(
            'change', data, 'pending', '')
        self.assertEqual('pending', status)
        self.assertEqual('', address)
        self.assertFalse(mock_print.called)


class TestParseUnitChange(helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_unit_removed(self):
        # A ValueError is raised if the change represents a unit removal.
        data = {'Name': 'django/42', 'Status': 'started'}
        with self.assert_value_error('django/42 unexpectedly removed'):
            # The last argument is the current status.
            watchers.parse_unit_change('remove', data, '')

    def test_unit_error(self):
        # A ValueError is raised if the unit is in an error state.
        data = {
            'Name': 'django/0',
            'Status': 'start error',
            'StatusInfo': 'bad wolf',
        }
        expected_error = 'django/0 is in an error state: start error: bad wolf'
        with self.assert_value_error(expected_error):
            # The last argument is the current status.
            watchers.parse_unit_change('change', data, '')

    @helpers.mock_print
    def test_pending_status_notified(self, mock_print):
        # A message is printed to stdout when the unit changes its status to
        # "pending". The function returns the new status and the machine
        # identifier, which is empty if the unit has not yet been assigned to a
        # machine.
        data = {'Name': 'django/1', 'Status': 'pending'}
        # The last argument is the current status.
        status, machine_id = watchers.parse_unit_change('change', data, '')
        self.assertEqual('pending', status)
        self.assertEqual('', machine_id)
        mock_print.assert_called_once_with('django/1 deployment is pending')

    @helpers.mock_print
    def test_installed_status_notified(self, mock_print):
        # A message is printed to stdout when the unit changes its status to
        # "installed".
        data = {'Name': 'django/42', 'Status': 'installed', 'MachineId': '1'}
        status, machine_id = watchers.parse_unit_change(
            'change', data, 'pending')
        self.assertEqual('installed', status)
        self.assertEqual('1', machine_id)
        mock_print.assert_called_once_with('django/42 is installed')

    @helpers.mock_print
    def test_started_status_notified(self, mock_print):
        # A message is printed to stdout when the unit changes its status to
        # "started".
        data = {'Name': 'wordpress/0', 'Status': 'started', 'MachineId': '0'}
        # The last argument is the current status.
        status, machine_id = watchers.parse_unit_change('change', data, '')
        self.assertEqual('started', status)
        self.assertEqual('0', machine_id)
        mock_print.assert_called_once_with('wordpress/0 is ready on machine 0')

    @helpers.mock_print
    def test_status_not_changed(self, mock_print):
        # If the status in the unit change and the given current status are the
        # same value, nothing is printed and the current values are returned.
        data = {'Name': 'django/1', 'Status': 'pending'}
        status, machine_id = watchers.parse_unit_change(
            'change', data, 'pending')
        self.assertEqual('pending', status)
        self.assertEqual('', machine_id)
        self.assertFalse(mock_print.called)


class TestUnitMachineChanges(unittest.TestCase):

    def test_unit_changes_found(self):
        # Unit changes are correctly found and returned.
        data1 = {'Name': 'django/42', 'Status': 'started'}
        data2 = {'Name': 'django/47', 'Status': 'pending'}
        changeset = [('unit', 'change', data1), ('unit', 'remove', data2)]
        expected_unit_changes = [('change', data1), ('remove', data2)]
        self.assertEqual(
            (expected_unit_changes, []),
            watchers.unit_machine_changes(changeset))

    def test_machine_changes_found(self):
        # Machine changes are correctly found and returned.
        data1 = {'Id': '0', 'Status': 'started'}
        data2 = {'Id': '1', 'Status': 'error'}
        changeset = [
            ('machine', 'change', data1),
            ('machine', 'remove', data2),
        ]
        expected_machine_changes = [('change', data1), ('remove', data2)]
        self.assertEqual(
            ([], expected_machine_changes),
            watchers.unit_machine_changes(changeset))

    def test_unit_and_machine_changes_found(self):
        # Changes to unit and machines are reordered, grouped and returned.
        machine_data1 = {'Id': '0', 'Status': 'started'}
        machine_data2 = {'Id': '42', 'Status': 'started'}
        unit_data1 = {'Name': 'django/42', 'Status': 'error'}
        unit_data2 = {'Name': 'haproxy/47', 'Status': 'pending'}
        unit_data3 = {'Name': 'wordpress/0', 'Status': 'installed'}
        changeset = [
            ('machine', 'change', machine_data1),
            ('unit', 'change', unit_data1),
            ('machine', 'remove', machine_data2),
            ('unit', 'change', unit_data2),
            ('unit', 'remove', unit_data3),
        ]
        expected_unit_changes = [
            ('change', unit_data1),
            ('change', unit_data2),
            ('remove', unit_data3),
        ]
        expected_machine_changes = [
            ('change', machine_data1),
            ('remove', machine_data2),
        ]
        self.assertEqual(
            (expected_unit_changes, expected_machine_changes),
            watchers.unit_machine_changes(changeset))

    def test_other_entities(self):
        # Changes to other entities (like services) are ignored.
        machine_data = {'Id': '0', 'Status': 'started'}
        unit_data = {'Name': 'django/42', 'Status': 'error'}
        changeset = [
            ('machine', 'change', machine_data),
            ('service', 'change', {'Name': 'django', 'Status': 'pending'}),
            ('unit', 'change', unit_data),
            ('service', 'remove', {'Name': 'haproxy', 'Status': 'started'}),
        ]
        expected_changes = (
            [('change', unit_data)],
            [('change', machine_data)],
        )
        self.assertEqual(
            expected_changes, watchers.unit_machine_changes(changeset))

    def test_empty_changeset(self):
        # Two empty lists are returned if the changeset is empty.
        # This should never occur in the real world, but it's tested here to
        # demonstrate this function behavior.
        self.assertEqual(([], []), watchers.unit_machine_changes([]))
