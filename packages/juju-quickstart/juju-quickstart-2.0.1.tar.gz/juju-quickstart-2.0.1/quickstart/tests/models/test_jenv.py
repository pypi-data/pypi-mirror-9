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

"""Tests for the Juju Quickstart jenv generated files handling."""

from __future__ import unicode_literals

import os
import unittest

import mock
import yaml

from quickstart.models import jenv
from quickstart.tests import helpers


class TestExists(helpers.JenvFileTestsMixin, unittest.TestCase):

    def test_found(self):
        # True is returned if the jenv file exists.
        with self.make_jenv('ec2', ''):
            exists = jenv.exists('ec2')
        self.assertTrue(exists)

    def test_not_found(self):
        # False is returned if the jenv file does not exist.
        with self.make_jenv('ec2', ''):
            exists = jenv.exists('local')
        self.assertFalse(exists)


class TestGetValue(
        helpers.JenvFileTestsMixin, helpers.ValueErrorTestsMixin,
        unittest.TestCase):

    def test_whole_content(self):
        # The function correctly returns the whole jenv content.
        with self.make_jenv('local', yaml.safe_dump(self.jenv_data)):
            data = jenv.get_value('local')
        self.assertEqual(self.jenv_data, data)

    def test_section(self):
        # The function correctly returns a whole section.
        with self.make_jenv('ec2', yaml.safe_dump(self.jenv_data)):
            data = jenv.get_value('ec2', 'bootstrap-config')
        self.assertEqual(self.jenv_data['bootstrap-config'], data)

    def test_value(self):
        # The function correctly returns a value in the root node.
        with self.make_jenv('ec2', yaml.safe_dump(self.jenv_data)):
            value = jenv.get_value('ec2', 'user')
        self.assertEqual('admin', value)

    def test_section_value(self):
        # The function correctly returns a section value.
        with self.make_jenv('ec2', yaml.safe_dump(self.jenv_data)):
            value = jenv.get_value('ec2', 'bootstrap-config', 'admin-secret')
        self.assertEqual('Secret!', value)

    def test_nested_section(self):
        # The function correctly returns nested section's values.
        with self.make_jenv('hp', yaml.safe_dump(self.jenv_data)):
            value = jenv.get_value('hp', 'life', 'universe', 'everything')
        self.assertEqual(42, value)

    def test_file_not_found(self):
        # A ValueError is raised if the jenv file cannot be found.
        expected_error = 'unable to open file'
        with self.make_jenv('hp', yaml.safe_dump(self.jenv_data)):
            with self.assertRaises(ValueError) as context_manager:
                jenv.get_value('local')
        self.assertIn(expected_error, bytes(context_manager.exception))

    def test_section_not_found(self):
        # A ValueError is raised if the specified section cannot be found.
        with self.make_jenv('local', yaml.safe_dump(self.jenv_data)) as path:
            expected_error = (
                'cannot read {}: invalid YAML contents: no-such key not found '
                'in the root section'.format(path))
            with self.assert_value_error(expected_error):
                jenv.get_value('local', 'no-such')

    def test_subsection_not_found(self):
        # A ValueError is raised if the specified subsection cannot be found.
        with self.make_jenv('local', yaml.safe_dump(self.jenv_data)) as path:
            expected_error = (
                'cannot read {}: invalid YAML contents: series key not found '
                'in the bootstrap-config section'.format(path))
            with self.assert_value_error(expected_error):
                jenv.get_value('local', 'bootstrap-config', 'series')

    def test_invalid_yaml_contents(self):
        # A ValueError is raised if the jenv file is not well formed.
        expected_error = 'unable to parse file'
        with self.make_jenv('ec2', ':'):
            with self.assertRaises(ValueError) as context_manager:
                jenv.get_value('ec2')
        self.assertIn(expected_error, bytes(context_manager.exception))


class TestGetCredentials(
        helpers.JenvFileTestsMixin, helpers.ValueErrorTestsMixin,
        unittest.TestCase):

    def test_valid_credentials(self):
        # The user name and password are correctly returned.
        data = {'user': 'jean-luc', 'password': 'Secret!'}
        with self.make_jenv('local', yaml.safe_dump(data)):
            username, password = jenv.get_credentials('local')
        self.assertEqual('jean-luc', username)
        self.assertEqual('Secret!', password)

    def test_default_user(self):
        # The default user name is returned if it's not possible to retrieve it
        # otherwise.
        data = {'password': 'Secret!'}
        with self.make_jenv('local', yaml.safe_dump(data)):
            expected_logs = [
                'cannot retrieve the user name: '
                'invalid YAML contents: '
                'user key not found in the root section: '
                'falling back to the default user name']
            with helpers.assert_logs(expected_logs, 'warn'):
                username, password = jenv.get_credentials('local')
        self.assertEqual('admin', username)
        self.assertEqual('Secret!', password)

    def test_using_admin_secret(self):
        # If the password is not found in the jenv file, the admin secret is
        # returned if present.
        data = {
            'user': 'who',
            'bootstrap-config': {'admin-secret': 'Admin!'},
        }
        with self.make_jenv('local', yaml.safe_dump(data)):
            expected_logs = [
                'cannot retrieve the password: '
                'invalid YAML contents: '
                'password key not found in the root section: '
                'trying with the admin-secret']
            with helpers.assert_logs(expected_logs, 'debug'):
                username, password = jenv.get_credentials('local')
        self.assertEqual('Admin!', password)

    def test_password_not_found(self):
        # A ValueError is raised if the password cannot be found anywhere.
        with self.make_jenv('local', yaml.safe_dump({})) as path:
            expected_error = (
                'cannot parse {}: '
                'cannot retrieve the password: '
                'invalid YAML contents: bootstrap-config key '
                'not found in the root section'.format(path))
            with self.assert_value_error(expected_error):
                jenv.get_credentials('local')


class TestGetEnvUuid(helpers.JenvFileTestsMixin, unittest.TestCase):

    def test_uuid_found(self):
        # The environment UUID is correctly returned when included in the jenv.
        with self.make_jenv('local', yaml.safe_dump(self.jenv_data)):
            env_uuid = jenv.get_env_uuid('local')
        self.assertEqual('__unique_identifier__', env_uuid)

    def test_uuid_not_found(self):
        # None is returned if the environment UUID is not present in the jenv.
        data = {'user': 'jean-luc', 'password': 'Secret!'}
        with self.make_jenv('local', yaml.safe_dump(data)):
            env_uuid = jenv.get_env_uuid('local')
        self.assertIsNone(env_uuid)

    def test_invalid_jenv(self):
        # A ValueError is raised if there are errors parsing the jenv file.
        expected_error = 'unable to parse file'
        with self.make_jenv('ec2', ':'):
            with self.assertRaises(ValueError) as context_manager:
                jenv.get_env_uuid('ec2')
        self.assertIn(expected_error, bytes(context_manager.exception))


class TestGetEnvDb(helpers.JenvFileTestsMixin, unittest.TestCase):

    def test_no_juju_home(self):
        # An empty db is returned if the Juju home is not set up.
        with mock.patch('quickstart.settings.JUJU_HOME', '/no/such/dir'):
            jenv_db = jenv.get_env_db()
        self.assertEqual({'environments': {}}, jenv_db)

    def test_no_jenv_files(self):
        # An empty db is returned if there are no jenv files.
        with self.make_multiple_jenvs({}):
            jenv_db = jenv.get_env_db()
        self.assertEqual({'environments': {}}, jenv_db)

    def test_no_valid_jenv_files(self):
        # An empty db is returned if there are no valid jenv files.
        with self.make_jenv('local', yaml.safe_dump({})):
            expected_logs = [
                'ignoring invalid jenv file local.jenv: '
                'cannot retrieve the password: invalid YAML contents: '
                'bootstrap-config key not found in the root section']
            with helpers.assert_logs(expected_logs, 'warn'):
                jenv_db = jenv.get_env_db()
        self.assertEqual({'environments': {}}, jenv_db)

    def test_single_valid_jenv(self):
        # Only the valid environments are returned.
        with self.make_multiple_jenvs({
            'local': yaml.safe_dump({}),
            'ec2': yaml.safe_dump(self.jenv_data),
        }):
            jenv_db = jenv.get_env_db()
        expected_environments = {
            'ec2': {
                'type': 'ec2',
                'user': 'admin',
                'state-servers': ('localhost:17070', '10.0.3.1:17070'),
            },
        }
        self.assertEqual({'environments': expected_environments}, jenv_db)

    def test_multiple_jenv_files(self):
        # Multiple environments are correctly returned.
        jenv_data1 = {
            'user': 'admin',
            'password': 'Secret!',
            'state-servers': ['localhost:17070'],
            'bootstrap-config': {'type': 'hp'},
        }
        jenv_data2 = {
            'user': 'my-user',
            'password': 'Secret!',
            'state-servers': ['1.2.3.4:5', '1.2.3.4:42'],
            'bootstrap-config': {'type': 'maas'},
        }
        with self.make_multiple_jenvs({
            'hp-cloud': yaml.safe_dump(jenv_data1),
            'maas': yaml.safe_dump(jenv_data2),
        }):
            jenv_db = jenv.get_env_db()
        expected_environments = {
            'hp-cloud': {
                'type': 'hp',
                'user': 'admin',
                'state-servers': ('localhost:17070',),
            },
            'maas': {
                'type': 'maas',
                'user': 'my-user',
                'state-servers': ('1.2.3.4:5', '1.2.3.4:42'),
            },
        }
        self.assertEqual({'environments': expected_environments}, jenv_db)

    def test_unknown_env_type(self):
        # If the jenv file does not include the env type, jenv.UNKNOWN_ENV_TYPE
        # is used as the environment type.
        jenv_data = {
            'user': 'admin',
            'password': 'Secret!',
            'state-servers': ['localhost:17070'],
        }
        with self.make_jenv('local', yaml.safe_dump(jenv_data)):
            jenv_db = jenv.get_env_db()
        expected_environments = {
            'local': {
                'type': jenv.UNKNOWN_ENV_TYPE,
                'user': 'admin',
                'state-servers': ('localhost:17070',),
            },
        }
        self.assertEqual({'environments': expected_environments}, jenv_db)

    def test_extraneous_files(self):
        # Extraneous files are ignored.
        with self.make_multiple_jenvs({}) as juju_home:
            envs_dir = os.path.join(juju_home, 'environments')
            os.mkdir(os.path.join(envs_dir, 'local.jenv'))
            with open(os.path.join(envs_dir, 'not-a-jenv'), 'w') as stream:
                stream.write('bad wolf')
            jenv_db = jenv.get_env_db()
        self.assertEqual({'environments': {}}, jenv_db)


class TestRemove(helpers.JenvFileTestsMixin, unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Prepare the jenv file contents.
        cls.contents = yaml.safe_dump(cls.jenv_data)

    def test_successful_removal(self):
        # The jenv file is correctly removed.
        with self.make_jenv('local', self.contents) as path:
            error = jenv.remove('local')
        self.assertIsNone(error)
        self.assertFalse(os.path.exists(path))

    def test_error_directory(self):
        # An error message is returned if the jenv path points to a directory.
        with self.make_jenv('local', self.contents) as path:
            dirname = os.path.dirname(path)
            os.mkdir(os.path.join(dirname, 'ec2.jenv'))
            error = jenv.remove('ec2')
        self.assertIn('cannot remove the ec2 environment: ', error)

    def test_error_not_found(self):
        # An error is returned if the environment cannot be found.
        with self.make_jenv('local', self.contents):
            error = jenv.remove('hp')
        expected_error = (
            'cannot remove the hp environment: '
            '[Errno 2] No such file or directory: ')
        self.assertIn(expected_error, error)


class TestValidate(
        helpers.JenvFileTestsMixin, helpers.ValueErrorTestsMixin,
        unittest.TestCase):

    def test_validation_success(self):
        # A valid jenv file is successfully validated.
        credentials, servers = jenv.validate(self.jenv_data)
        self.assertEqual(('admin', 'Secret!'), credentials)
        self.assertEqual(('localhost:17070', '10.0.3.1:17070'), servers)

    def test_invalid_credentials(self):
        # A ValueError is raised if the credentials cannot be retrieved.
        expected_error = (
            'cannot retrieve the password: invalid YAML contents: '
            'bootstrap-config key not found in the root section')
        with self.assert_value_error(expected_error):
            jenv.validate({})

    def test_missing_state_servers(self):
        # A ValueError is raised if the Juju state servers cannot be retrieved.
        with self.assert_value_error('invalid state-servers field'):
            jenv.validate({
                'user': 'admin',
                'password': 'Secret!',
            })

    def test_invalid_state_servers(self):
        # A ValueError is raised if the Juju servers have an invalid type.
        with self.assert_value_error('invalid state-servers field'):
            jenv.validate({
                'user': 'admin',
                'password': 'Secret!',
                'state-servers': 'NO!',
            })

    def test_no_state_servers(self):
        # A ValueError is raised if the state server list is empty.
        with self.assert_value_error('no state-servers found'):
            jenv.validate({
                'user': 'admin',
                'password': 'Secret!',
                'state-servers': [],
            })


class TestGetEnvShortDescription(unittest.TestCase):

    def test_env(self):
        # The env description includes the environment name and type.
        env_data = {'name': 'lxc', 'type': 'local'}
        description = jenv.get_env_short_description(env_data)
        self.assertEqual('lxc (type: local)', description)

    def test_env_without_type(self):
        # Without the type we can only show the environment name.
        env_data = {'name': 'ec2', 'type': jenv.UNKNOWN_ENV_TYPE}
        description = jenv.get_env_short_description(env_data)
        self.assertEqual('ec2', description)


class TestGetEnvDetails(unittest.TestCase):

    def test_env(self):
        # The environment details are properly returned.
        env_data = {
            'name': 'lxc',
            'type': 'local',
            'user': 'who',
            'state-servers': ('1.2.3.4:17060', 'localhost:17070'),
        }
        expected_details = [
            ('type', 'local'),
            ('name', 'lxc'),
            ('user', 'who'),
            ('state servers', '1.2.3.4:17060, localhost:17070'),
        ]
        details = jenv.get_env_details(env_data)
        self.assertEqual(expected_details, details)

    def test_env_without_type(self):
        # The environment type is not included if unknown.
        env_data = {
            'name': 'aws',
            'type': jenv.UNKNOWN_ENV_TYPE,
            'user': 'the-doctor',
            'state-servers': ('1.2.3.4:17060',),
        }
        expected_details = [
            ('name', 'aws'),
            ('user', 'the-doctor'),
            ('state servers', '1.2.3.4:17060'),
        ]
        details = jenv.get_env_details(env_data)
        self.assertEqual(expected_details, details)
