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

"""Juju Quickstart jenv generated files handling.

At bootstrap, Juju writes a generated file (jenv) located in JUJU_HOME.
This module includes functions to load and parse those jenv file contents.
"""

from __future__ import unicode_literals

import logging
import os

from quickstart import (
    serializers,
    settings,
)


# Define the default Juju user when an environment is initially bootstrapped.
JUJU_DEFAULT_USER = 'admin'
# Define an env type to use when the real type is not included in the jenv.
UNKNOWN_ENV_TYPE = '__unknown__'


def exists(env_name):
    """Report whether the jenv generated file exists for the given env_name."""
    jenv_path = _get_jenv_path(env_name)
    return os.path.isfile(jenv_path)


def get_value(env_name, *args):
    """Read a value from the Juju generated environment file (jenv).

    Return the value corresponding to the section specified in args.
    For instance, calling get_value('ec2', 'bootstrap-config', 'admin-secret')
    returns the value associated with the "admin-secret" key included on the
    "bootstrap-config" section of the jenv file.

    Raise a ValueError if:
        - the environment file is not found;
        - the environment file contents are not parsable by YAML;
        - the YAML contents are not properly structured;
        - one the keys in args is not found.
    """
    jenv_path = _get_jenv_path(env_name)
    data = serializers.yaml_load_from_path(jenv_path)
    try:
        return _get_value_from_yaml(data, *args)
    except ValueError as err:
        raise ValueError(
            b'cannot read {}: {}'.format(jenv_path.encode('utf-8'), err))


def get_credentials(env_name):
    """Return the Juju environment credentials stored in the jenv file.

    The credentials are returned as a tuple (username, password).
    Note that the returned user name is not prefixed with the Juju default
    prefix for user entities ("user-).

    Raise a ValueError if:
        - the environment file is not found;
        - the environment file contents are not parsable by YAML;
        - the credentials cannot be found.
    """
    jenv_path = _get_jenv_path(env_name)
    data = serializers.yaml_load_from_path(jenv_path)
    try:
        return _get_credentials(data)
    except ValueError as err:
        msg = b'cannot parse {}: {}'.format(jenv_path.encode('utf-8'), err)
        raise ValueError(msg)


def _get_credentials(data):
    """Return the Juju environment credentials from the YAML decoded data.

    Raise a ValueError if the credentials cannot be found.
    See get_credentials for further information on how the credentials are
    retrieved.
    """
    # Retrieve the user name.
    try:
        username = _get_value_from_yaml(data, 'user')
    except ValueError as err:
        # This is probably an old version of Juju not supporting multiple
        # users. Return the default user name.
        logging.warn(
            b'cannot retrieve the user name: {}: '
            b'falling back to the default user name'.format(err))
        username = JUJU_DEFAULT_USER

    # Retrieve the password.
    try:
        password = _get_value_from_yaml(data, 'password')
    except ValueError as err:
        # This is probably an old version of Juju not supporting multiple
        # users. Fall back to the admin secret.
        msg = b'cannot retrieve the password: '
        logging.debug(msg + bytes(err) + ': trying with the admin-secret')
        try:
            password = _get_value_from_yaml(
                data, 'bootstrap-config', 'admin-secret')
        except ValueError as err:
            raise ValueError(msg + bytes(err))

    return username, password


def get_env_uuid(env_name):
    """Return the Juju environment unique identifier.

    Return None if the environment UUID is not included in the jenv file.
    Raise a ValueError if:
        - the environment file is not found;
        - the environment file contents are not parsable by YAML.
    """
    jenv_path = _get_jenv_path(env_name)
    data = serializers.yaml_load_from_path(jenv_path)
    try:
        return _get_value_from_yaml(data, 'environ-uuid')
    except ValueError:
        # This is probably an old version of Juju.
        return None


def get_env_db():
    """Return an environment database parsing the existing jenv files.

    The returned db is similar to what is returned by models.envs.load().

    When a jenv file is created using "juju user add", the resulting YAML data
    is very concise, not even including the environment type.
    For this reason, the environment database returned by this function does
    not contain the usual fields used as bootstrap options.
    The included fields are: "name", "type", "user" and "state-servers".

    If the environment type is not included in the jenv, UNKNOWN_ENV_TYPE is
    used.
    """
    db = {'environments': {}}
    path = os.path.expanduser(os.path.join(settings.JUJU_HOME, 'environments'))
    # Check if the Juju home is already configured.
    if not os.path.isdir(path):
        logging.debug('environments directory not found in the Juju home')
        return db
    # Collect the environments.
    environments = db['environments']
    for filename in os.listdir(path):
        fullpath = os.path.join(path, filename)
        # Check that the current file is a jenv file.
        if not os.path.isfile(fullpath):
            continue
        name, ext = os.path.splitext(filename)
        if ext != '.jenv':
            continue
        # Validate the jenv contents.
        try:
            data = serializers.yaml_load_from_path(fullpath)
            credentials, servers = validate(data)
        except ValueError as err:
            logging.warn('ignoring invalid jenv file {}: {}'. format(
                filename, bytes(err).decode('utf-8')))
            continue
        # Try to retrieve the environment type from the jenv data.
        try:
            env_type = _get_value_from_yaml(data, 'bootstrap-config', 'type')
        except ValueError:
            # This is expected when a jenv is generated with "juju user add".
            env_type = UNKNOWN_ENV_TYPE
        environments[name] = {
            'type': env_type,
            'user': credentials[0],
            'state-servers': servers,
        }
    return db


def remove(env_name):
    """Remove the jenv file corresponding to the given environment name.

    Return None if the removal was successful, an error message otherwise.
    """
    jenv_path = _get_jenv_path(env_name)
    try:
        os.remove(jenv_path)
    except OSError as err:
        msg = 'cannot remove the {} environment: {}'
        return msg.format(env_name, bytes(err).decode('utf-8'))
    return None


def validate(data):
    """Validate the given YAML decoded jenv data.

    This is a weak validation: from the quickstart point of view a jenv file is
    valid if it includes the juju environment credentials and the API servers.

    Raise a ValueError if:
        - the environment file is not found;
        - the environment file contents are not parsable by YAML;
        - the environment data is not valid.

    Return the environment credentials and state servers.
    """
    credentials = _get_credentials(data)
    servers = _get_state_servers(data)
    if not len(servers):
        raise ValueError(b'no state-servers found')
    return credentials, servers


def get_env_short_description(env_data):
    """Return a short description of the given env_data.

    The given env_data must include at least the "name" and "type" keys.
    """
    parts = [env_data['name']]
    env_type = env_data['type']
    if env_type != UNKNOWN_ENV_TYPE:
        parts.append('(type: {})'.format(env_type))
    return ' '.join(parts)


def get_env_details(env_data):
    """Return the environment details as a sequence of tuples (label, value).

    In each tuple, the label is the field name, and the value is the
    corresponding value in the given env_data.
    """
    details = []
    # Add the environment type.
    env_type = env_data['type']
    if env_type != UNKNOWN_ENV_TYPE:
        details.append(('type', env_type))
    # Add the environment name and user.
    details.extend([
        ('name', env_data['name']),
        ('user', env_data['user']),
    ])
    # Add the state servers.
    servers = ', '.join(env_data['state-servers'])
    details.append(('state servers', servers))
    return details


def _get_state_servers(data):
    """Return a tuple of Juju state servers for the given jenv data.

    Raise a ValueError if the state servers cannot be retrieved.
    """
    servers = data.get('state-servers')
    if not isinstance(servers, (list, tuple)):
        raise ValueError(b'invalid state-servers field')
    return tuple(servers)


def _get_value_from_yaml(data, *args):
    """Read and return a value from the given YAML decoded data.

    Return the value corresponding to the specified args sequence.
    For instance, if args is ('bootstrap-config', 'admin-secret'), the value
    associated with the "admin-secret" key included on the "bootstrap-config"
    section is returned.

    Raise a ValueError if:
        - the YAML contents are not properly structured;
        - one the keys in args is not found.
    """
    section = 'root'
    for key in args:
        try:
            data = data[key]
        except (KeyError, TypeError):
            msg = ('invalid YAML contents: {} key not found in the {} section'
                   ''.format(key, section))
            raise ValueError(msg.encode('utf-8'))
        section = key
    return data


def _get_jenv_path(env_name):
    """Return the path to the generated jenv file for the given env_name."""
    filename = '{}.jenv'.format(env_name)
    path = os.path.join(settings.JUJU_HOME, 'environments', filename)
    return os.path.expanduser(path)
