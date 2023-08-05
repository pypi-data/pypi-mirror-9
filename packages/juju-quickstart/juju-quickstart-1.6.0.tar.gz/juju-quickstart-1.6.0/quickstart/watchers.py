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

"""Juju Quickstart utilities for watching Juju environments."""

from __future__ import (
    print_function,
    unicode_literals,
)

import logging

from quickstart import netutils


IPV4_ADDRESS = 'ipv4'
IPV6_ADDRESS = 'ipv6'
SCOPE_CLOUD_LOCAL = 'local-cloud'
SCOPE_PUBLIC = 'public'
SCOPE_UNKNOWN = ''


def retrieve_public_adddress(addresses, hostname_resolver):
    """Parse the given addresses and return a public address if available.

    Use the given hostname_resolver callable to ensure a candidate address can
    be resolved. The given function must accept an hostname/ip address and
    return None if the address is resolvable, or an error string otherwise.

    The addresses argument is a list of address dictionaries.
    Cloud addresses look like the following:

        [
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

    When using the local provider, LXC addresses are like the following:

        [
            {'NetworkName': '',
             'Scope': '',
             'Type': 'ipv4',
             'Value': '10.0.3.42'},
            {'NetworkName': '',
             'Scope': '',
             'Type': 'ipv6',
             'Value': 'fe80::216:3eff:fefd:787e'},
        ]

    If the addresses list is empty, or if no public/reachable addresses can be
    found, this function returns None.
    """
    # This implementation reflects how the public address is retrieved in Juju:
    # see juju-core/network/address.go:SelectPublicAddress.
    fallback_address = None
    for address in addresses:
        value = address['Value']
        # Exclude empty values and ipv6 addresses.
        if value and (address['Type'] != IPV6_ADDRESS):
            # The address scope was called "NetworkScope" prior to juju 1.20.0.
            scope = address.get('Scope', address.get('NetworkScope'))
            # If the scope is public then we have found the address.
            if scope == SCOPE_PUBLIC:
                error = hostname_resolver(value)
                if error is None:
                    return value
                # If the address is not resolvable, fall back to the next
                # candidate, whether it is another public address, a
                # local-cloud one or an unknown one. The local-cloud case, for
                # instance, would happen when using the maas provider and the
                # maas DNS server is not configured locally.
                logging.warn(
                    'cannot resolve public {} address, looking for another '
                    'candidate: {}'.format(value, error))
            if fallback_address is not None:
                # If we already have a fallback address then we can jump to the
                # next candidate.
                continue
            address_type = address.get('Type')
            if scope == SCOPE_CLOUD_LOCAL and address_type == IPV4_ADDRESS:
                # Use the local cloud scoped address as fallback value: the
                # current environment is probably maas and the public address
                # of the instance is not resolvable by local DNS.
                fallback_address = value
            elif scope == SCOPE_UNKNOWN:
                # Use the unknown scoped address as fallback value: the current
                # environment is probably local.
                fallback_address = value
    return fallback_address


def parse_machine_change(action, data, current_status, address):
    """Parse the given machine change.

    The change is represented by the given action/data pair.
    Also receive the last known machine status and address, which can be empty
    strings if those pieces of information are unknown.

    Output a human readable message each time a relevant change is found.

    Return the machine status and the address.
    Raise a ValueError if the machine is removed or in an error state.
    """
    machine_id = data['Id']
    status = data['Status']
    # Exit with an error if the machine is removed.
    if action == 'remove':
        msg = 'machine {} unexpectedly removed'.format(machine_id)
        raise ValueError(msg.encode('utf-8'))
    if 'error' in status:
        msg = 'machine {} is in an error state: {}: {}'.format(
            machine_id, status, data['StatusInfo'])
        raise ValueError(msg.encode('utf-8'))
    # Notify when the machine becomes reachable. Starting from juju-core 1.18,
    # the mega-watcher for machines includes addresses for each machine. This
    # info is the preferred source where to look to retrieve the public address
    # of units hosted by a specific machine.
    if not address:
        addresses = data.get('Addresses', [])
        public_address = retrieve_public_adddress(
            addresses, netutils.check_resolvable)
        if public_address is not None:
            address = public_address
            print('unit placed on {}'.format(address))
    # Notify status changes.
    if status != current_status:
        if status == 'pending':
            print('machine {} provisioning is pending'.format(
                machine_id))
        elif status == 'started':
            print('machine {} is started'.format(machine_id))
    return status, address


def parse_unit_change(action, data, current_status):
    """Parse the given unit change.

    The change is represented by the given action/data pair.
    Also receive the last known unit status which can be empty if the unit
    status is not yet known.

    Output a human readable message each time a relevant change is found.

    Return the unit status and the identifier of the machine hosting the unit.
    Raise a ValueError if the service unit is removed or in an error state.
    """
    unit_name = data['Name']
    # Exit with an error if the unit is removed.
    if action == 'remove':
        msg = '{} unexpectedly removed'.format(unit_name)
        raise ValueError(msg.encode('utf-8'))
    # Exit with an error if the unit is in an error state.
    status = data['Status']
    if 'error' in status:
        msg = '{} is in an error state: {}: {}'.format(
            unit_name, status, data['StatusInfo'])
        raise ValueError(msg.encode('utf-8'))
    # Notify status changes.
    if status != current_status:
        if status == 'pending':
            print('{} deployment is pending'.format(unit_name))
        elif status == 'installed':
            print('{} is installed'.format(unit_name))
        elif status == 'started':
            print('{} is ready on machine {}'.format(
                unit_name, data['MachineId']))
    return status, data.get('MachineId', '')


def unit_machine_changes(changeset):
    """Parse the changeset and return the units and machines related changes.

    Changes to units and machines are grouped into two lists, e.g.:

        unit_changes, machine_changes = unit_machine_changes(changeset)

    Each list includes (action, data) tuples, in which:
        - action is he change type (e.g. "change", "remove");
        - data is the actual information about the changed entity (as a dict).

    This function is intended to be used as a processor callable for the
    watch_changes method of quickstart.juju.Environment.
    """
    unit_changes = []
    machine_changes = []
    for entity, action, data in changeset:
        if entity == 'unit':
            unit_changes.append((action, data))
        elif entity == 'machine':
            machine_changes.append((action, data))
    return unit_changes, machine_changes
