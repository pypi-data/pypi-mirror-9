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

"""Quickstart utility functions for managing Juju environments and entities."""

from __future__ import (
    print_function,
    unicode_literals,
)

import logging

from quickstart import (
    serializers,
    settings,
)
from quickstart.models import references


def get_api_url(
        api_address, juju_version, env_uuid, prefix='', charm_ref=None):
    """Return the Juju WebSocket API endpoint.

    Receives the Juju API server address, the Juju version and the unique
    identifier of the current environment.

    Optionally receive a prefix to be used in the path.

    Optionally also receive the Juju GUI charm reference as an instance of
    "quickstart.models.references.Reference". If provided, the function checks
    that the corresponding Juju GUI charm supports the new Juju API endpoint.
    If not supported, the old endpoint is returned.

    The environment UUID can be None, in which case the old-style API URL
    (not including the environment UUID) is returned.
    """
    base_url = 'wss://{}'.format(api_address)
    prefix = prefix.strip('/')
    if prefix:
        base_url = '{}/{}'.format(base_url, prefix)
    if (env_uuid is None) or (juju_version < (1, 22, 0)):
        return base_url
    complete_url = '{}/environment/{}/api'.format(base_url, env_uuid)
    if charm_ref is None:
        return complete_url
    # If a customized Juju GUI charm is in use, there is no way to check if the
    # GUI server is recent enough to support the new Juju API endpoints.
    # In these cases, assume the customized charm is recent enough.
    if (
        charm_ref.name != settings.JUJU_GUI_CHARM_NAME or
        charm_ref.user or
        charm_ref.is_local()
    ):
        return complete_url
    # This is the promulgated Juju GUI charm. Check if it supports new APIs.
    revision, series = charm_ref.revision, charm_ref.series
    if revision < settings.MINIMUM_REVISIONS_FOR_NEW_API_ENDPOINT[series]:
        return base_url
    return complete_url


def get_service_info(status, service_name):
    """Retrieve information on the given service and on its first alive unit.

    Return a tuple containing two values: (service data, unit data).
    Each value can be:
        - a dictionary of data about the given entity (service or unit) as
          returned by the Juju watcher;
        - None, if the entity is not present in the Juju environment.
    If the service data is None, the unit data is always None.
    """
    services = [
        data for entity, action, data in status if
        (entity == 'service') and (action != 'remove') and
        (data['Name'] == service_name) and (data['Life'] == 'alive')
    ]
    if not services:
        return None, None
    units = [
        data for entity, action, data in status if
        entity == 'unit' and action != 'remove' and
        data['Service'] == service_name
    ]
    return services[0], units[0] if units else None


def parse_gui_charm_url(charm_url):
    """Parse the given charm URL.

    Check if the charm URL seems to refer to a Juju GUI charm.
    Print (to stdout or to logs) info and warnings about the charm URL.

    Return the parsed charm reference object as an instance of
    "quickstart.models.references.Reference".
    """
    print('charm URL: {}'.format(charm_url))
    ref = references.Reference.from_fully_qualified_url(charm_url)
    charm_name = settings.JUJU_GUI_CHARM_NAME
    if ref.name != charm_name:
        # This does not seem to be a Juju GUI charm.
        logging.warn(
            'unexpected URL for the {} charm: '
            'the service may not work as expected'.format(charm_name))
        return ref
    if ref.user or ref.is_local():
        # This is not the official Juju GUI charm.
        logging.warn('using a customized {} charm'.format(charm_name))
    elif ref.revision < settings.MINIMUM_REVISIONS_FOR_BUNDLES[ref.series]:
        # This is the official Juju GUI charm, but it is outdated.
        logging.warn(
            'charm is outdated and may not support bundle deployments')
    return ref


def parse_status_output(output, keys=None):
    """Parse the output of juju status.

    Return selection specified by the keys array.
    Raise a ValueError if the selection cannot be retrieved.
    """
    if keys is None:
        keys = ['dummy']
    try:
        status = serializers.yaml_load(output)
    except Exception as err:
        raise ValueError(b'unable to parse the output: {}'.format(err))

    selection = status
    for key in keys:
        try:
            selection = selection.get(key, {})
        except AttributeError as err:
            msg = 'invalid YAML contents: {}'.format(status)
            raise ValueError(msg.encode('utf-8'))
    if selection == {}:
        msg = '{} not found in {}'.format(':'.join(keys), status)
        raise ValueError(msg.encode('utf-8'))
    return selection


def get_agent_state(output):
    """Parse the output of juju status for the agent state.

    Return the agent state.
    Raise a ValueError if the agent state cannot be retrieved.
    """
    return parse_status_output(output, ['machines', '0', 'agent-state'])


def get_bootstrap_node_series(output):
    """Parse the output of juju status for the agent state.

    Return the agent state.
    Raise a ValueError if the agent state cannot be retrieved.
    """
    return parse_status_output(output, ['machines', '0', 'series'])
