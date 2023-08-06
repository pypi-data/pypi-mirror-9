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

"""Test helpers for the Juju Quickstart plugin."""

from __future__ import unicode_literals

from contextlib import contextmanager
import os
import shutil
import socket
import tempfile

import mock
import yaml


@contextmanager
def assert_logs(messages, level='debug'):
    """Ensure the given messages are logged using the given log level.

    Use this function as a context manager: the code executed in the context
    block must add the expected log entries.
    """
    with mock.patch('logging.{}'.format(level.lower())) as mock_log:
        yield
    if messages:
        expected_calls = [mock.call(message) for message in messages]
        mock_log.assert_has_calls(expected_calls)
    else:
        assert not mock_log.called, 'logging unexpectedly called'


class BundleFileTestsMixin(object):
    """Shared methods for testing Juju bundle files."""

    bundle_data = {'services': {'wordpress': {}, 'mysql': {}}}
    bundle_content = yaml.safe_dump(bundle_data)
    legacy_bundle_data = {
        'bundle1': {'services': {'wordpress': {}, 'mysql': {}}},
        'bundle2': {'services': {'django': {}, 'nodejs': {}}},
    }
    legacy_bundle_content = yaml.safe_dump(legacy_bundle_data)

    def _write_bundle_file(self, bundle_file, contents):
        """Parse and write contents into the given bundle file object."""
        if contents is None:
            contents = self.bundle_content
        elif isinstance(contents, dict):
            contents = yaml.safe_dump(contents)
        bundle_file.write(contents)

    def make_bundle_file(self, contents=None):
        """Create a Juju bundle file containing the given contents.

        If contents is None, use the valid bundle contents defined in
        self.bundle_content.
        Return the bundle file path.
        """
        bundle_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        self.addCleanup(os.remove, bundle_file.name)
        self._write_bundle_file(bundle_file, contents)
        bundle_file.close()
        return bundle_file.name


class CallTestsMixin(object):
    """Easily use the quickstart.utils.call function."""

    def patch_call(self, retcode, output='', error=''):
        """Patch the quickstart.utils.call function."""
        mock_call = mock.Mock(return_value=(retcode, output, error))
        return mock.patch('quickstart.utils.call', mock_call)

    def patch_multiple_calls(self, side_effect):
        """Patch multiple subsequent quickstart.utils.call calls."""
        mock_call = mock.Mock(side_effect=side_effect)
        return mock.patch('quickstart.utils.call', mock_call)


class EnvFileTestsMixin(object):
    """Shared methods for testing a Juju environments file."""

    valid_contents = yaml.safe_dump({
        'default': 'aws',
        'environments': {
            'aws': {
                'admin-secret': 'Secret!',
                'type': 'ec2',
                'default-series': 'saucy',
                'access-key': 'AccessKey',
                'secret-key': 'SeceretKey',
                'control-bucket': 'ControlBucket',
            },
        },
    })

    def make_env_file(self, contents=None):
        """Create a Juju environments file containing the given contents.

        If contents is None, use the valid environment contents defined in
        self.valid_contents.
        Return the environments file path.
        """
        if contents is None:
            contents = self.valid_contents
        env_file = tempfile.NamedTemporaryFile(delete=False)
        self.addCleanup(os.remove, env_file.name)
        env_file.write(contents)
        env_file.close()
        return env_file.name


class JenvFileTestsMixin(object):
    """Shared methods for testing Juju generated environment files (jenv)."""

    jenv_data = {
        'user': 'admin',
        'password': 'Secret!',
        'environ-uuid': '__unique_identifier__',
        'state-servers': ['localhost:17070', '10.0.3.1:17070'],
        'bootstrap-config': {
            'admin-secret': 'Secret!',
            'api-port': 17070,
            'type': 'ec2',
        },
        'life': {'universe': {'everything': 42}},
    }

    def _make_playground(self):
        """Create and return a mock Juju home."""
        playground = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, playground)
        os.mkdir(os.path.join(playground, 'environments'))
        return playground

    def write_jenv(self, juju_home, name, contents):
        """Create a jenv file in the given Juju home.

        Use the given name and YAML encoded contents to create the jenv.
        Return the resulting jenv path.
        """
        path = os.path.join(juju_home, 'environments', '{}.jenv'.format(name))
        with open(path, 'w') as jenv_file:
            jenv_file.write(contents)
        return path

    @contextmanager
    def make_jenv(self, env_name, contents):
        """Create a temporary jenv file with the given env_name and contents.

        In the context manager block, the JUJU_HOME is set to the ancestor
        of the generated temporary file.

        Return the jenv file path.
        """
        playground = self._make_playground()
        jenv_path = self.write_jenv(playground, env_name, contents)
        # Patch the JUJU_HOME and return the jenv file path.
        with mock.patch('quickstart.settings.JUJU_HOME', playground):
            yield jenv_path

    @contextmanager
    def make_multiple_jenvs(self, data):
        """Create multiple temporary jenv files with the data.

        Data is a dict mapping env names to jenv contents.

        In the context manager block, the JUJU_HOME is set to the ancestor
        of the generated temporary files.

        Return the Juju home path.
        """
        playground = self._make_playground()
        for name, contents in data.items():
            self.write_jenv(playground, name, contents)
        # Patch the JUJU_HOME and return the jenv file path.
        with mock.patch('quickstart.settings.JUJU_HOME', playground):
            yield playground


def make_env_db(default=None, exclude_invalid=False):
    """Create and return an env_db.

    The default argument can be used to specify a default environment.
    If exclude_invalid is set to True, the resulting env_db only includes
    valid environments.
    """
    environments = {
        'ec2-west': {
            'type': 'ec2',
            'admin-secret': 'adm-307c4a53bd174c1a89e933e1e8dc8131',
            'control-bucket': 'con-aa2c6618b02d448ca7fd0f280ef66cba',
            'region': u'us-west-1',
            'access-key': 'hash',
            'secret-key': 'Secret!',
        },
        'lxc': {
            'admin-secret': 'bones',
            'default-series': 'raring',
            'storage-port': 8888,
            'type': 'local',
        },
        'test-encoding': {
            'access-key': '\xe0\xe8\xec\xf2\xf9',
            'secret-key': '\xe0\xe8\xec\xf2\xf9',
            'admin-secret': '\u2622\u2622\u2622\u2622',
            'control-bucket': '\u2746 winter-bucket \u2746',
            'juju-origin': '\u2606 the outer space \u2606',
            'type': 'toxic \u2622 type',
        },
    }
    if not exclude_invalid:
        environments.update({
            'local-with-errors': {
                'admin-secret': '',
                'storage-port': 'this-should-be-an-int',
                'type': 'local',
            },
            'private-cloud-errors': {
                'admin-secret': 'Secret!',
                'auth-url': 'https://keystone.example.com:443/v2.0/',
                'authorized-keys-path': '/home/frankban/.ssh/juju-rsa.pub',
                'control-bucket': 'e3d48007292c9abba499d96a577ceab891d320fe',
                'default-image-id': 'bb636e4f-79d7-4d6b-b13b-c7d53419fd5a',
                'default-instance-type': 'm1.medium',
                'default-series': 'no-such',
                'type': 'openstack',
            },
        })
    env_db = {'environments': environments}
    if default is not None:
        env_db['default'] = default
    return env_db


def make_jenv_db():
    """Create and return a jenv files database."""
    environments = {
        'ec2-west': {
            'type': '__unknown__',
            'user': 'who',
            'state-servers': ('1.2.3.4:42', '1.2.3.4:47'),
        },
        'lxc': {
            'type': 'local',
            'user': 'dalek',
            'state-servers': ('localhost:17070', '10.0.3.1:17070'),
        },
        'test-jenv': {
            'type': '__unknown__',
            'user': 'my-user',
            'state-servers': ('10.0.3.1:17070',),
        },
    }
    return {'environments': environments}


# Mock the builtin print function.
mock_print = mock.patch('__builtin__.print')


def patch_socket_create_connection(error=None):
    """Patch the socket.create_connection function.

    If error is not None, the mock object raises a socket.error with the given
    message.
    """
    mock_create_connection = mock.Mock()
    if error is not None:
        mock_create_connection.side_effect = socket.error(error)
    return mock.patch('socket.create_connection', mock_create_connection)


def patch_check_resolvable(error=None):
    """Patch the netutils.check_resolvable function to return the given error.

    This is done so that tests do not try to resolve hostname addresses.
    """
    return mock.patch(
        'quickstart.netutils.check_resolvable',
        lambda hostname: error,
    )


class UrlReadTestsMixin(object):
    """Helpers to mock the quickstart.netutils.urlread helper function."""

    def patch_urlread(self, contents=None, error=False):
        """Patch the quickstart.netutils.urlread helper function.

        If contents is not None, urlread() will return the provided contents.
        If error is set to True, an IOError will be simulated.
        """
        mock_urlread = mock.Mock()
        if contents is not None:
            mock_urlread.return_value = contents
        if error:
            mock_urlread.side_effect = IOError('bad wolf')
        return mock.patch('quickstart.netutils.urlread', mock_urlread)


class ValueErrorTestsMixin(object):
    """Set up some base methods for testing functions raising ValueErrors."""

    @contextmanager
    def assert_value_error(self, error):
        """Ensure a ValueError is raised in the context block.

        Also check that the exception includes the expected error message.
        """
        with self.assertRaises(ValueError) as context_manager:
            yield
        self.assertEqual(error, bytes(context_manager.exception))


class WatcherDataTestsMixin(object):
    """Shared methods for testing Juju mega-watcher data."""

    def make_service_data(self, data=None):
        """Create and return a data dictionary for a service.

        The passed data can be used to override default values.
        """
        default_data = {
            'CharmURL': 'cs:precise/juju-gui-47',
            'Exposed': True,
            'Life': 'alive',
            'Name': 'my-gui',
        }
        if data is not None:
            default_data.update(data)
        return default_data

    def make_service_change(self, action='change', data=None):
        """Create and return a change on a service.

        The passed data can be used to override default values.
        """
        return 'service', action, self.make_service_data(data)

    def make_unit_data(self, data=None):
        """Create and return a data dictionary for a unit.

        The passed data can be used to override default values.
        """
        default_data = {'Name': 'my-gui/47', 'Service': 'my-gui'}
        if data is not None:
            default_data.update(data)
        return default_data

    def make_unit_change(self, action='change', data=None):
        """Create and return a change on a unit.

        The passed data can be used to override default values.
        """
        return 'unit', action, self.make_unit_data(data)
