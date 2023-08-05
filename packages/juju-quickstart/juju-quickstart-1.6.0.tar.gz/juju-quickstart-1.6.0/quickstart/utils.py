# This file is part of the Juju Quickstart Plugin, which lets users set up a
# Juju environment in very few steps (https://launchpad.net/juju-quickstart).
# Copyright (C) 2013-2014 Canonical Ltd.
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

"""Juju Quickstart utility functions and classes."""

from __future__ import (
    print_function,
    unicode_literals,
)

import collections
import datetime
import errno
import functools
import logging
import os
import pipes
import re
import subprocess

import quickstart
from quickstart import (
    serializers,
    settings,
)
from quickstart.models import charms


# Compile the regular expression used to parse bundle URLs.
_bundle_expression = re.compile(r"""
    # Bundle schema or bundle URL namespace on jujucharms.com.
    ^(?:bundle:|{})
    (?:~([-\w]+)/)?  # Optional user name.
    ([-\w]+)/  # Basket name.
    (?:(\d+)/)?  # Optional bundle revision number.
    ([-\w]+)  # Bundle name.
    /?$  # Optional trailing slash.
""".format(settings.JUJUCHARMS_BUNDLE_URL), re.VERBOSE)


def add_apt_repository(repository):
    """Add the given APT repository to the current list of APT sources.

    Also take care of installing the add-apt-repository script and of updating
    the list of APT packages after the repository installation.

    Raise an OSError if any error occur in the process.
    """
    print('adding the {} PPA repository'.format(repository))
    print('sudo privileges will be required for PPA installation')
    # The package including add-apt-repository is python-software-properties
    # in precise and software-properties-common after precise.
    add_repository_package = 'software-properties-common'
    if get_ubuntu_codename() == 'precise':
        add_repository_package = 'python-software-properties'
    commands = (
        ('/usr/bin/apt-get', 'install', '-y', add_repository_package),
        ('/usr/bin/add-apt-repository', '-y', repository),
        ('/usr/bin/apt-get', 'update'),
    )
    for command in commands:
        retcode, _, error = call('sudo', *command)
        if retcode:
            raise OSError(error.encode('utf-8'))


def call(command, *args):
    """Call a subprocess passing the given arguments.

    Take the subcommand and its parameters as args.

    Return a tuple containing the subprocess return code, output and error.
    """
    pipe = subprocess.PIPE
    cmd = (command,) + args
    cmdline = ' '.join(map(pipes.quote, cmd))
    logging.debug('running the following: {}'.format(cmdline))
    try:
        process = subprocess.Popen(cmd, stdout=pipe, stderr=pipe)
    except OSError as err:
        # A return code 127 is returned by the shell when the command is not
        # found in the PATH.
        return 127, '', '{}: {}'.format(command, err)
    output, error = process.communicate()
    retcode = process.poll()
    logging.debug('retcode: {} | output: {!r} | error: {!r}'.format(
        retcode, output, error))
    return retcode, output.decode('utf-8'), error.decode('utf-8')


def parse_gui_charm_url(charm_url):
    """Parse the given charm URL.

    Check if the charm looks like a Juju GUI charm.
    Print (to stdout or to logs) info and warnings about the charm URL.

    Return the parsed charm object as an instance of
    quickstart.models.charms.Charm.
    """
    print('charm URL: {}'.format(charm_url))
    charm = charms.Charm.from_url(charm_url)
    charm_name = settings.JUJU_GUI_CHARM_NAME
    if charm.name != charm_name:
        # This does not seem to be a Juju GUI charm.
        logging.warn(
            'unexpected URL for the {} charm: '
            'the service may not work as expected'.format(charm_name))
        return charm
    if charm.user or charm.is_local():
        # This is not the official Juju GUI charm.
        logging.warn('using a customized {} charm'.format(charm_name))
    elif charm.revision < settings.MINIMUM_REVISIONS_FOR_BUNDLES[charm.series]:
        # This is the official Juju GUI charm, but it is outdated.
        logging.warn(
            'charm is outdated and may not support bundle deployments')
    return charm


def convert_bundle_url(bundle_url):
    """Return the equivalent YAML HTTPS location for the given bundle URL.

    Raise a ValueError if the given URL is not a valid bundle URL.
    """
    match = _bundle_expression.match(bundle_url)
    if match is None:
        msg = 'invalid bundle URL: {}'.format(bundle_url)
        raise ValueError(msg.encode('utf-8'))
    user, basket, revision, name = match.groups()
    user_part = '~charmers/' if user is None else '~{}/'.format(user)
    revision_part = '' if revision is None else '{}/'.format(revision)
    bundle_id = '{}{}/{}{}'.format(user_part, basket, revision_part, name)
    return ('https://manage.jujucharms.com/bundle/{}/json'.format(bundle_id),
            bundle_id)


def get_quickstart_banner():
    """Return a quickstart banner suitable for being included in files.

    The banner is returned as a string, e.g.:

        # This file has been generated by juju quickstart v0.42.0
        # in date 2013-12-31 23:59:00 UTC.
    """
    now = datetime.datetime.utcnow()
    formatted_date = now.isoformat(sep=b' ').split('.')[0]
    version = quickstart.get_version()
    return (
        '# This file has been generated by juju quickstart v{}\n'
        '# at {} UTC.\n\n'.format(version, formatted_date))


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


def get_ubuntu_codename():
    """Return the codename of the current Ubuntu release (e.g. "trusty").

    Raise an OSError if an error occurs retrieving the codename.
    """
    retcode, output, error = call('lsb_release', '-cs')
    if retcode:
        raise OSError(error.encode('utf-8'))
    return output.strip()


def mkdir(path):
    """Create a leaf directory and all intermediate ones.

    Also expand ~ and ~user constructions.
    If path exists and it's a directory, return without errors.
    """
    path = os.path.expanduser(path)
    try:
        os.makedirs(path)
    except OSError as err:
        # Re-raise the error if the target path exists but it is not a dir.
        if (err.errno != errno.EEXIST) or (not os.path.isdir(path)):
            raise


def parse_bundle(bundle_yaml, bundle_name=None):
    """Parse the provided bundle YAML encoded contents.

    Since a valid JSON is a subset of YAML this function can be used also to
    parse JSON encoded contents.

    Return a tuple containing the bundle name and the list of services included
    in the bundle.

    Raise a ValueError if:
      - the bundle YAML contents are not parsable by YAML;
      - the YAML contents are not properly structured;
      - the bundle name is specified but not included in the bundle file;
      - the bundle name is not specified and the bundle file includes more than
        one bundle;
      - the bundle does not include services.
    """
    # Parse the bundle file.
    try:
        bundles = serializers.yaml_load(bundle_yaml)
    except Exception as err:
        msg = b'unable to parse the bundle: {}'.format(err)
        raise ValueError(msg)
    # Ensure the bundle file is well formed and contains at least one bundle.
    if not isinstance(bundles, collections.Mapping):
        msg = 'invalid YAML contents: {}'.format(bundle_yaml)
        raise ValueError(msg.encode('utf-8'))
    try:
        name_services_map = dict(
            (key, value['services'].keys())
            for key, value in bundles.items()
        )
    except (AttributeError, KeyError, TypeError):
        msg = 'invalid YAML contents: {}'.format(bundle_yaml)
        raise ValueError(msg.encode('utf-8'))
    if not name_services_map:
        raise ValueError(b'no bundles found')
    # Retrieve the bundle name and services.
    if bundle_name is None:
        if len(name_services_map) > 1:
            msg = 'multiple bundles found ({}) but no bundle name specified'
            bundle_names = ', '.join(sorted(name_services_map.keys()))
            raise ValueError(msg.format(bundle_names).encode('utf-8'))
        bundle_name, bundle_services = name_services_map.items()[0]
    else:
        bundle_services = name_services_map.get(bundle_name)
        if bundle_services is None:
            msg = 'bundle {} not found in the provided list of bundles ({})'
            bundle_names = ', '.join(sorted(name_services_map.keys()))
            raise ValueError(
                msg.format(bundle_name, bundle_names).encode('utf-8'))
    if not bundle_services:
        msg = 'bundle {} does not include any services'.format(bundle_name)
        raise ValueError(msg.encode('utf-8'))
    if settings.JUJU_GUI_SERVICE_NAME in bundle_services:
        msg = ('bundle {} contains an instance of juju-gui. quickstart will '
               'install the latest version of the Juju GUI automatically, '
               'please remove juju-gui from the bundle.'.format(bundle_name))
        raise ValueError(msg.encode('utf-8'))
    return bundle_name, bundle_services


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


def get_juju_version(juju_command):
    """Return the current juju-core version.

    Return a (major:int, minor:int, patch:int) tuple, including major, minor
    and patch version numbers.

    Handle the special case of no patch level by defaulting to 0.

    Raise a ValueError if the "juju version" call exits with an error
    or the returned version is not well formed.
    """
    retcode, output, error = call(juju_command, 'version')
    if retcode:
        raise ValueError(error.encode('utf-8'))
    version_string = output.split('-')[0]
    try:
        parts = version_string.split('.', 2)
        if len(parts) == 2:
            parts.append(0)
        major, minor, patch = map(int, parts)
        return major, minor, patch
    except ValueError:
        msg = 'invalid version string: {}'.format(version_string)
        raise ValueError(msg.encode('utf-8'))


def run_once(function):
    """Return a decorated version of the given function which runs only once.

    Subsequent runs are just ignored and return None.
    """
    @functools.wraps(function)
    def decorated(*args, **kwargs):
        if not decorated.called:
            decorated.called = True
            return function(*args, **kwargs)
    decorated.called = False
    return decorated
