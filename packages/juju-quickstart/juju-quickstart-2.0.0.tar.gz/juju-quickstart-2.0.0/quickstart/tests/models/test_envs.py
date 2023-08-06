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

"""Tests for the Juju Quickstart environments management."""

from __future__ import unicode_literals

import collections
import copy
import functools
import os
import shutil
import tempfile
import unittest

import mock
import yaml

from quickstart import settings
from quickstart.models import (
    envs,
    fields,
)
from quickstart.tests import helpers


class TestGetDefaultEnvName(helpers.CallTestsMixin, unittest.TestCase):

    def test_environment_variable(self):
        # The environment name is successfully returned if JUJU_ENV is set.
        with mock.patch('os.environ', {'JUJU_ENV': 'ec2'}):
            env_name = envs.get_default_env_name()
        self.assertEqual('ec2', env_name)

    def test_empty_environment_variable(self):
        # The environment name is not found if JUJU_ENV is empty.
        with self.patch_call(1):
            with mock.patch('os.environ', {'JUJU_ENV': ' '}):
                env_name = envs.get_default_env_name()
        self.assertIsNone(env_name)

    def test_no_environment_variable(self):
        # The environment name is not found if JUJU_ENV is not defined.
        with self.patch_call(1):
            with mock.patch('os.environ', {}):
                env_name = envs.get_default_env_name()
        self.assertIsNone(env_name)

    def test_juju_switch_old_behavior(self):
        # The environment name is successfully returned if retrievable using
        # the "juju switch" command. This test exercises the old "juju switch"
        # returning a human readable output.
        output = 'Current environment: "hp"\n'
        with self.patch_call(0, output=output) as mock_call:
            with mock.patch('os.environ', {}):
                env_name = envs.get_default_env_name()
        self.assertEqual('hp', env_name)
        mock_call.assert_called_once_with('juju', 'switch')

    def test_juju_switch_new_behavior(self):
        # The environment name is successfully returned if retrievable using
        # the "juju switch" command. This test exercises the new "juju switch"
        # returning a machine readable output (just the name of the env).
        # This new behavior has been introduced in juju-core 1.17.
        output = 'ec2\n'
        with self.patch_call(0, output=output) as mock_call:
            with mock.patch('os.environ', {}):
                env_name = envs.get_default_env_name()
        self.assertEqual('ec2', env_name)
        mock_call.assert_called_once_with('juju', 'switch')

    def test_juju_switch_failure(self):
        # The environment name is not found if "juju switch" returns an error.
        with self.patch_call(1) as mock_call:
            with mock.patch('os.environ', {}):
                env_name = envs.get_default_env_name()
        self.assertIsNone(env_name)
        mock_call.assert_called_once_with('juju', 'switch')


class TestCreateEmptyEnvDb(unittest.TestCase):

    def test_resulting_env_db(self):
        # The function surprisingly returns an empty environments database.
        env_db = envs.create_empty_env_db()
        self.assertEqual({'environments': {}}, env_db)


class TestLoad(
        helpers.EnvFileTestsMixin, helpers.ValueErrorTestsMixin,
        unittest.TestCase):

    def test_empty_file(self):
        # An empty environments database is returned if the file is empty.
        env_file = self.make_env_file('')
        env_db = envs.load(env_file)
        self.assertEqual({'environments': {}}, env_db)

    def test_invalid_yaml_contents(self):
        # A ValueError is raised if the environments file is not well formed.
        env_file = self.make_env_file('a-string')
        expected = 'invalid YAML contents in {}: a-string'.format(env_file)
        with self.assert_value_error(expected):
            envs.load(env_file)

    def test_success_with_default(self):
        # The YAML decoded environments dictionary (including default) is
        # correctly generated and returned.
        env_file = self.make_env_file()
        env_db = envs.load(env_file)
        self.assertEqual(yaml.safe_load(self.valid_contents), env_db)

    def test_success_no_default(self):
        # The YAML decoded environments dictionary (with no default) is
        # correctly generated and returned.
        expected = {
            'environments': {
                'aws': {'admin-secret': 'Secret!', 'type': 'ec2'},
                'local': {'admin-secret': 'Secret!', 'type': 'local'},
            },
        }
        env_file = self.make_env_file(yaml.safe_dump(expected))
        env_db = envs.load(env_file)
        self.assertEqual(expected, env_db)

    def test_success_invalid_default(self):
        # The YAML decoded environments dictionary is correctly generated and
        # returned excluding invalid default environment values.
        expected = {
            'environments': {
                'aws': {'admin-secret': 'Secret!', 'type': 'ec2'},
            },
        }
        yaml_contents = expected.copy()
        yaml_contents['default'] = 'no-such-env'
        expected_logs = ['excluding invalid default no-such-env']
        env_file = self.make_env_file(yaml.safe_dump(yaml_contents))
        with helpers.assert_logs(expected_logs, 'warn'):
            env_db = envs.load(env_file)
        self.assertEqual(expected, env_db)

    def test_success_extraneous_fields(self):
        # The YAML decoded environments dictionary is correctly generated and
        # returned preserving extraneous fields.
        expected = {
            'environments': {
                'aws': {'polluted': True, 'type': 'ec2'},
                'local': {'answer': 42},
            },
        }
        env_file = self.make_env_file(yaml.safe_dump(expected))
        env_db = envs.load(env_file)
        self.assertEqual(expected, env_db)

    def test_success_excluding_envs(self):
        # The YAML decoded environments dictionary is correctly generated and
        # returned excluding invalid environments.
        expected = {
            'default': 'aws',
            'environments': {
                'aws': {'admin-secret': 'Secret!', 'type': 'ec2'},
            },
        }
        yaml_contents = copy.deepcopy(expected)
        yaml_contents['environments']['bad'] = 42
        expected_logs = ['excluding invalid environment bad']
        env_file = self.make_env_file(yaml.safe_dump(yaml_contents))
        with helpers.assert_logs(expected_logs, 'warn'):
            env_db = envs.load(env_file)
        self.assertEqual(expected, env_db)


class TestSave(helpers.EnvFileTestsMixin, unittest.TestCase):

    def setUp(self):
        # Create an environments file.
        self.env_file = self.make_env_file()
        self.original_contents = open(self.env_file).read()

    def make_juju_home(self):
        """Create a temporary Juju home directory.

        Return the Juju home path and the path of the corresponding
        environments file.
        """
        playground = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, playground)
        juju_home = os.path.join(playground, '.juju')
        os.mkdir(juju_home)
        return juju_home, os.path.join(juju_home, 'environments.yaml')

    def test_dump_error(self):
        # An OSError is raised if errors occur in the serialization process.
        with mock.patch('quickstart.serializers.yaml_dump') as mock_yaml_dump:
            mock_yaml_dump.side_effect = ValueError(b'bad wolf')
            with self.assertRaises(OSError) as context_manager:
                envs.save(self.env_file, {'new': 'contents'})
        self.assertEqual(b'bad wolf', str(context_manager.exception))
        # The original file contents have been left untouched.
        self.assertEqual(self.valid_contents, self.original_contents)

    def test_atomic(self):
        # The new contents are written in a temporary file before and then the
        # file is renamed to the original destination. If an error occurs, the
        # original contents are not influenced.
        def rename(source, destination):
            # Remove the source before actually renaming in order to simulate
            # some kind of disk error.
            os.remove(source)
            os.rename(source, destination)
        with mock.patch('os.rename', rename):
            with self.assertRaises(OSError) as context_manager:
                envs.save(self.env_file, {'new': 'contents'})
        self.assertIn(
            'No such file or directory',
            str(context_manager.exception))
        # The original file contents have been left untouched.
        self.assertEqual(self.valid_contents, self.original_contents)

    def test_success(self):
        # The environments file is correctly updated with the new contents.
        envs.save(self.env_file, {'new': 'contents'})
        contents = open(self.env_file).read()
        # The banner has been written.
        self.assertIn(
            '# This file has been generated by juju quickstart',
            contents)
        # Also the new contents have been saved.
        self.assertIn('new: contents', contents)

    def test_backup(self):
        # A backup function, if provided, is used to create a backup copy
        # of the original environments file.
        mock_backup = mock.Mock()
        envs.save(
            self.env_file, {'new': 'contents'}, backup_function=mock_backup)
        contents = open(self.env_file).read()
        expected_backup_path = self.env_file + '.quickstart.bak'
        # The backup function has been called.
        mock_backup.assert_called_once_with(
            self.env_file, expected_backup_path)
        # The new file indicates where to find the backup copy.
        self.assertIn(
            '# A backup copy of this file can be found in\n'
            '# {}\n'.format(expected_backup_path),
            contents)

    def test_missing_juju_home(self):
        # The environments file directory is created if not existing.
        juju_home, env_file = self.make_juju_home()
        shutil.rmtree(juju_home)
        envs.save(env_file, {'new': 'contents'})
        self.assertTrue(os.path.isdir(juju_home))

    def test_backup_missing_juju_home(self):
        # The backup function is not executed if there is nothing to backup.
        juju_home, env_file = self.make_juju_home()
        mock_backup = mock.Mock()
        envs.save(env_file, {'new': 'contents'}, backup_function=mock_backup)
        self.assertFalse(mock_backup.called)


class EnvDataTestsMixin(object):
    """Set up an initial environments dictionary."""

    def setUp(self):
        self.env_db = {
            'default': 'lxc',
            'environments': {
                'aws': {
                    'admin_secret': 'Secret!',
                    'default-series': 'precise',
                    'type': 'ec2',
                },
                'lxc': {
                    'admin_secret': 'NotSoSecret!',
                    'mutable': [1, 2, 3],
                    'type': 'local',
                },
            },
        }
        self.original = copy.deepcopy(self.env_db)
        super(EnvDataTestsMixin, self).setUp()

    def assert_env_db_not_modified(self):
        """Ensure the stored env_db is not modified."""
        self.assertEqual(self.original, self.env_db)


class TestGetEnvData(
        EnvDataTestsMixin, helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_env_not_found(self):
        # A ValueError is raised if an environment with the given name is not
        # found in the environments dictionary.
        with self.assert_value_error("environment no-such not found"):
            envs.get_env_data(self.env_db, 'no-such')

    def test_resulting_env_data(self):
        # The resulting env_data is correctly generated.
        expected = {
            'admin_secret': 'Secret!',
            'default-series': 'precise',
            'is-default': False,
            'name': 'aws',
            'type': 'ec2',
        }
        obtained = envs.get_env_data(self.env_db, 'aws')
        self.assertEqual(expected, obtained)

    def test_env_data_default_environments(self):
        # The env_data is correctly generated for a default environment.
        expected = {
            'admin_secret': 'NotSoSecret!',
            'is-default': True,
            'mutable': [1, 2, 3],
            'name': 'lxc',
            'type': 'local',
        }
        obtained = envs.get_env_data(self.env_db, 'lxc')
        self.assertEqual(expected, obtained)

    def test_mutate(self):
        # Modifications to the resulting env_data do not influence the original
        # environments dictionary.
        env_data = envs.get_env_data(self.env_db, 'lxc')
        env_data.update({
            'admin_secret': 'AnotherSecret!',
            'is-default': False,
            'new-field': 'new-value'
        })
        # Also change a mutable internal data structure.
        env_data['mutable'].append(42)
        self.assert_env_db_not_modified()


class TestSetEnvData(
        EnvDataTestsMixin, helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_error_no_name_key(self):
        # A ValueError is raised if the env_data dictionary does not include
        # the "name" key.
        env_data = {'is-default': False}
        expected = "invalid env_data: {u'is-default': False}"
        with self.assert_value_error(expected):
            envs.set_env_data(self.env_db, 'aws', env_data)
        # The environments dictionary has not been modified.
        self.assert_env_db_not_modified()

    def test_error_no_default_key(self):
        # A ValueError is raised if the env_data dictionary does not include
        # the "is-default" key.
        env_data = {'name': 'aws'}
        expected = "invalid env_data: {u'name': u'aws'}"
        with self.assert_value_error(expected):
            envs.set_env_data(self.env_db, 'aws', env_data)
        # The environments dictionary has not been modified.
        self.assert_env_db_not_modified()

    def test_error_new_environment(self):
        # A ValueError is raised if the name of a new environment is
        # already in the environments dictionary.
        env_data = {'is-default': False, 'name': 'aws'}
        expected = "an environment named u'aws' already exists"
        with self.assert_value_error(expected):
            envs.set_env_data(self.env_db, None, env_data)
        # The environments dictionary has not been modified.
        self.assert_env_db_not_modified()

    def test_error_existing_environment(self):
        # A ValueError is raised if the new name of a renamed existing
        # environment is already in the environments dictionary.
        env_data = {'is-default': False, 'name': 'lxc'}
        expected = "an environment named u'lxc' already exists"
        with self.assert_value_error(expected):
            envs.set_env_data(self.env_db, 'aws', env_data)
        # The environments dictionary has not been modified.
        self.assert_env_db_not_modified()

    def test_new_environment_added(self):
        # A new environment is properly added to the environments dictionary.
        env_data = {
            'default-series': 'edgy',
            'is-default': False,
            'name': 'new-one',
        }
        return_value = envs.set_env_data(self.env_db, None, env_data)
        self.assertIsNone(return_value)
        expected = {
            'default': 'lxc',
            'environments': {
                'aws': {
                    'admin_secret': 'Secret!',
                    'default-series': 'precise',
                    'type': 'ec2',
                },
                'lxc': {
                    'admin_secret': 'NotSoSecret!',
                    'mutable': [1, 2, 3],
                    'type': 'local',
                },
                'new-one': {
                    'default-series': 'edgy',
                },
            },
        }
        self.assertEqual(expected, self.env_db)

    def test_new_default_environment_added(self):
        # A new default environment is properly added to the environments
        # dictionary.
        env_data = {
            'default-series': 'edgy',
            'is-default': True,
            'name': 'new-one',
        }
        envs.set_env_data(self.env_db, None, env_data)
        self.assertIn('new-one', self.env_db['environments'])
        self.assertEqual(
            {'default-series': 'edgy'},
            self.env_db['environments']['new-one'])
        self.assertEqual('new-one', self.env_db['default'])

    def test_new_environment_with_no_default(self):
        # A new environment is properly added in an env_db with no default.
        env_data = {
            'default-series': 'edgy',
            'is-default': False,
            'name': 'new-one',
        }
        del self.env_db['default']
        envs.set_env_data(self.env_db, None, env_data)
        self.assertEqual(
            {'default-series': 'edgy'},
            self.env_db['environments']['new-one'])
        self.assertNotIn('default', self.env_db)

    def test_existing_environment_updated(self):
        # An existing environment is properly updated.
        env_data = {
            'admin_secret': 'NewSecret!',
            'is-default': True,
            'name': 'lxc',
            'type': 'local'
        }
        return_value = envs.set_env_data(self.env_db, 'lxc', env_data)
        self.assertIsNone(return_value)
        expected = {
            'default': 'lxc',
            'environments': {
                'aws': {
                    'admin_secret': 'Secret!',
                    'default-series': 'precise',
                    'type': 'ec2',
                },
                'lxc': {
                    'admin_secret': 'NewSecret!',
                    'type': 'local',
                },
            },
        }
        self.assertEqual(expected, self.env_db)

    def test_existing_environment_updated_changing_name(self):
        # An existing environment is properly updated, including its name.
        env_data = {
            'admin_secret': 'Hash!',
            'is-default': False,
            'name': 'yay-the-clouds',
            'type': 'ec2'
        }
        return_value = envs.set_env_data(self.env_db, 'aws', env_data)
        self.assertIsNone(return_value)
        expected = {
            'default': 'lxc',
            'environments': {
                'lxc': {
                    'admin_secret': 'NotSoSecret!',
                    'mutable': [1, 2, 3],
                    'type': 'local',
                },
                'yay-the-clouds': {
                    'admin_secret': 'Hash!',
                    'type': 'ec2',
                },
            },
        }
        self.assertEqual(expected, self.env_db)

    def test_existing_environment_set_as_default(self):
        # An existing environment is correctly promoted as the default one.
        env_data = {
            'default-series': 'edgy',
            'is-default': True,
            'name': 'aws',
        }
        envs.set_env_data(self.env_db, 'aws', env_data)
        self.assertIn('aws', self.env_db['environments'])
        self.assertEqual(
            {'default-series': 'edgy'},
            self.env_db['environments']['aws'])
        self.assertEqual('aws', self.env_db['default'])

    def test_existing_environment_no_longer_default(self):
        # An existing environment is correctly downgraded to non-default.
        env_data = {
            'default-series': 'edgy',
            'is-default': False,
            'name': 'lxc',
        }
        envs.set_env_data(self.env_db, 'lxc', env_data)
        self.assertIn('lxc', self.env_db['environments'])
        self.assertEqual(
            {'default-series': 'edgy'},
            self.env_db['environments']['lxc'])
        self.assertNotIn('default', self.env_db)


class TestCreateLocalEnvData(unittest.TestCase):

    def setUp(self):
        # Store the env_type_db.
        self.env_type_db = envs.get_env_type_db()

    def test_not_default(self):
        # The resulting env_data is correctly structured for non default envs.
        env_data = envs.create_local_env_data(
            self.env_type_db, 'my-lxc', is_default=False)
        # The function is not pure: auto-generated values change each time the
        # function is called. For local environments, the only auto-generated
        # value should be the admin-secret.
        admin_secret = env_data.pop('admin-secret', '')
        self.assertNotEqual(0, len(admin_secret))
        expected_env_data = {
            'type': 'local',
            'name': 'my-lxc',
            'is-default': False,
            'default-series': settings.JUJU_GUI_SUPPORTED_SERIES[-1],
        }
        self.assertEqual(expected_env_data, env_data)

    def test_default(self):
        # The resulting env_data is correctly structured for default envs.
        env_data = envs.create_local_env_data(
            self.env_type_db, 'my-default', is_default=True)
        # See the comment about auto-generated fields in the test method above.
        admin_secret = env_data.pop('admin-secret', '')
        self.assertNotEqual(0, len(admin_secret))
        expected_env_data = {
            'type': 'local',
            'name': 'my-default',
            'is-default': True,
            'default-series': settings.JUJU_GUI_SUPPORTED_SERIES[-1],
        }
        self.assertEqual(expected_env_data, env_data)


class TestCreateMaasEnvData(unittest.TestCase):

    def setUp(self):
        # Store the env_type_db.
        self.env_type_db = envs.get_env_type_db()

    def test_not_default(self):
        # The resulting env_data is correctly structured for non default envs.
        env_data = envs.create_maas_env_data(
            self.env_type_db, 'my-maas', 'http://1.2.3.4/MAAS', 'Secret!',
            is_default=False)
        expected_env_data = {
            'type': 'maas',
            'name': 'my-maas',
            'maas-server': 'http://1.2.3.4/MAAS',
            'maas-oauth': 'Secret!',
            'is-default': False,
        }
        self.assertEqual(expected_env_data, env_data)

    def test_default(self):
        # The resulting env_data is correctly structured for default envs.
        env_data = envs.create_maas_env_data(
            self.env_type_db, 'another-maas', 'http://1.2.3.4/MAAS', 'Boo!',
            is_default=True)
        expected_env_data = {
            'type': 'maas',
            'name': 'another-maas',
            'maas-server': 'http://1.2.3.4/MAAS',
            'maas-oauth': 'Boo!',
            'is-default': True,
        }
        self.assertEqual(expected_env_data, env_data)


class TestRemoveEnv(
        EnvDataTestsMixin, helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_removal(self):
        # An environment is successfully removed from the environments db.
        envs.remove_env(self.env_db, 'aws')
        environments = self.env_db['environments']
        self.assertNotIn('aws', environments)
        # The other environments are not removed.
        self.assertIn('lxc', environments)
        # The default environment is not modified.
        self.assertEqual('lxc', self.env_db['default'])

    def test_default_environment_removal(self):
        # An environment is successfully removed even if it is the default one.
        environments = self.env_db['environments']
        environments['a-third-one'] = {'type': 'openstack'}
        envs.remove_env(self.env_db, 'lxc')
        self.assertNotIn('lxc', environments)
        # The other environments are not removed.
        self.assertIn('aws', environments)
        # Since there are two remaining environments, the environments database
        # no longer includes a default environment.
        self.assertNotIn('default', self.env_db)

    def test_one_remaining_environment(self):
        # If, after a removal, only one environment remains, it is
        # automatically set as default.
        envs.remove_env(self.env_db, 'lxc')
        self.assertEqual(1, len(self.env_db['environments']))
        self.assertEqual('aws', self.env_db['default'])

    def test_remove_all_environments(self):
        # Removing all the environments results in an empty environments db.
        for env_name in list(self.env_db['environments'].keys()):
            envs.remove_env(self.env_db, env_name)
        self.assertEqual(envs.create_empty_env_db(), self.env_db)

    def test_invalid_environment_name(self):
        # A ValueError is raised if the environment is not present in env_db.
        expected = "the environment named u'no-such' does not exist"
        with self.assert_value_error(expected):
            envs.remove_env(self.env_db, 'no-such')


class TestGetEnvTypeDb(unittest.TestCase):

    def setUp(self):
        self.env_type_db = envs.get_env_type_db()

    def assert_fields(self, expected, env_metadata):
        """Ensure the expected fields are defined as part of env_metadata."""
        obtained = [field.name for field in env_metadata['fields']]
        self.assertEqual(expected, obtained)

    def assert_required_fields(self, expected, env_metadata):
        """Ensure the expected required fields are included in env_metadata."""
        obtained = [
            field.name for field in env_metadata['fields'] if field.required
        ]
        self.assertEqual(expected, obtained)

    def test_required_metadata(self):
        # The returned data includes the required env_metadata for each
        # provider type key.
        self.assertNotEqual(0, len(self.env_type_db))
        for provider_type, env_metadata in self.env_type_db.items():
            # Check the label metadata (not present in the fallback provider).
            if provider_type != '__fallback__':
                self.assertIn('label', env_metadata, provider_type)
                self.assertIsInstance(
                    env_metadata['label'], unicode, provider_type)
            # Check the description metadata.
            self.assertIn('description', env_metadata, provider_type)
            self.assertIsInstance(
                env_metadata['description'], unicode, provider_type)
            # Check the fields metadata.
            self.assertIn('fields', env_metadata)
            self.assertIsInstance(
                env_metadata['fields'], collections.Iterable, provider_type)

    def test_fallback(self):
        # A fallback provider type is included.
        self.assertIn('__fallback__', self.env_type_db)
        env_metadata = self.env_type_db['__fallback__']
        expected = [
            'type', 'name', 'admin-secret', 'default-series', 'is-default']
        expected_required = ['type', 'name', 'is-default']
        self.assert_fields(expected, env_metadata)
        self.assert_required_fields(expected_required, env_metadata)

    def test_local_environment(self):
        # The local environment metadata includes the expected fields.
        self.assertIn('local', self.env_type_db)
        env_metadata = self.env_type_db['local']
        expected = [
            'type', 'name', 'lxc-clone', 'lxc-clone-aufs', 'root-dir',
            'storage-port', 'shared-storage-port', 'network-bridge',
            'admin-secret', 'default-series', 'is-default']
        expected_required = ['type', 'name', 'is-default']
        self.assert_fields(expected, env_metadata)
        self.assert_required_fields(expected_required, env_metadata)

    def test_ec2_environment(self):
        # The ec2 environment metadata includes the expected fields.
        self.assertIn('ec2', self.env_type_db)
        env_metadata = self.env_type_db['ec2']
        expected = [
            'type', 'name', 'access-key', 'secret-key', 'region',
            'admin-secret', 'default-series', 'control-bucket', 'is-default']
        expected_required = [
            'type', 'name', 'access-key', 'secret-key',
            'is-default']
        self.assert_fields(expected, env_metadata)
        self.assert_required_fields(expected_required, env_metadata)

    def test_openstack_environment(self):
        # The openstack environment metadata includes the expected fields.
        self.assertIn('openstack', self.env_type_db)
        env_metadata = self.env_type_db['openstack']
        expected = [
            'type', 'name', 'auth-url', 'tenant-name', 'use-floating-ip',
            'region', 'auth-mode', 'username', 'password', 'access-key',
            'secret-key', 'control-bucket', 'admin-secret', 'default-series',
            'is-default']
        expected_required = [
            'type', 'name', 'auth-url', 'tenant-name', 'use-floating-ip',
            'region', 'is-default']
        self.assert_fields(expected, env_metadata)
        self.assert_required_fields(expected_required, env_metadata)

    def test_azure_environment(self):
        # The azure environment metadata includes the expected fields.
        self.assertIn('azure', self.env_type_db)
        env_metadata = self.env_type_db['azure']
        expected = [
            'type', 'name', 'management-subscription-id',
            'management-certificate-path', 'storage-account-name', 'location',
            'admin-secret', 'default-series', 'is-default']
        expected_required = [
            'type', 'name', 'management-subscription-id',
            'management-certificate-path', 'storage-account-name', 'location',
            'is-default']
        self.assert_fields(expected, env_metadata)
        self.assert_required_fields(expected_required, env_metadata)

    def test_joyent_environment(self):
        # The joyent environment metadata includes the expected fields.
        self.assertIn('joyent', self.env_type_db)
        env_metadata = self.env_type_db['joyent']
        expected = [
            'type', 'name', 'sdc-user', 'sdc-key-id', 'sdc-url', 'manta-user',
            'manta-key-id', 'manta-url', 'private-key-path', 'algorithm',
            'admin-secret', 'default-series', 'is-default']
        expected_required = [
            'type', 'name', 'sdc-user', 'sdc-key-id', 'manta-user',
            'manta-key-id', 'is-default']
        self.assert_fields(expected, env_metadata)
        self.assert_required_fields(expected_required, env_metadata)

    def test_maas_environment(self):
        # The MAAS environment metadata includes the expected fields.
        self.assertIn('maas', self.env_type_db)
        env_metadata = self.env_type_db['maas']
        expected = [
            'type', 'name', 'maas-server', 'maas-oauth',
            'authorized-keys-path', 'admin-secret', 'default-series',
            'is-default']
        expected_required = [
            'type', 'name', 'maas-server', 'maas-oauth', 'is-default']
        self.assert_fields(expected, env_metadata)
        self.assert_required_fields(expected_required, env_metadata)

    def test_manual_environment(self):
        # The manual environment metadata includes the expected fields.
        self.assertIn('manual', self.env_type_db)
        env_metadata = self.env_type_db['manual']
        expected = [
            'type', 'name', 'bootstrap-host', 'bootstrap-user',
            'storage-listen-ip', 'storage-port', 'admin-secret', 'is-default']
        expected_required = [
            'type', 'name', 'bootstrap-host', 'is-default']
        self.assert_fields(expected, env_metadata)
        self.assert_required_fields(expected_required, env_metadata)


class TestGetSupportedEnvTypes(unittest.TestCase):

    def setUp(self):
        # Store the environments database.
        self.env_type_db = envs.get_env_type_db()

    def test_env_types(self):
        # All the supported env_types but the fallback one are returned.
        expected_env_types = [
            ('ec2', 'Amazon EC2'),
            ('openstack', 'OpenStack (or HP Public Cloud)'),
            ('azure', 'Windows Azure'),
            ('joyent', 'Joyent'),
            ('maas', 'MAAS (bare metal)'),
            ('manual', 'Manual Provisioning'),
            ('local', 'local (LXC)'),
        ]
        obtained_env_types = envs.get_supported_env_types(self.env_type_db)
        self.assertEqual(expected_env_types, obtained_env_types)

    def test_filter_function(self):
        # Results can be filtered by providing a filter function.
        expected_env_types = [
            ('ec2', 'Amazon EC2'),
            ('joyent', 'Joyent'),
        ]
        func = lambda env_type, metadata: env_type in ('ec2', 'joyent')
        obtained_env_types = envs.get_supported_env_types(
            self.env_type_db, filter_function=func)
        self.assertEqual(expected_env_types, obtained_env_types)


class TestGetEnvMetadata(unittest.TestCase):

    def setUp(self):
        self.env_type_db = envs.get_env_type_db()

    def test_supported_environment(self):
        # The metadata for a supported environment is properly returned.
        env_data = {'type': 'local'}
        env_metadata = envs.get_env_metadata(self.env_type_db, env_data)
        self.assertEqual(self.env_type_db['local'], env_metadata)

    def test_unsupported_environment(self):
        # The metadata for an unsupported environment is properly returned.
        env_data = {'type': 'no-such'}
        env_metadata = envs.get_env_metadata(self.env_type_db, env_data)
        self.assertEqual(self.env_type_db['__fallback__'], env_metadata)

    def test_without_type(self):
        # The fallback metadata is also used when the env_data does not include
        # the provider type.
        env_metadata = envs.get_env_metadata(self.env_type_db, {})
        self.assertEqual(self.env_type_db['__fallback__'], env_metadata)


class TestMapFieldsToEnvData(unittest.TestCase):

    def setUp(self):
        env_type_db = envs.get_env_type_db()
        self.get_meta = functools.partial(envs.get_env_metadata, env_type_db)

    def assert_name_value_pairs(self, expected, env_data):
        """Ensure the expected field name/value pairs are included in env_data.
        """
        pairs = envs.map_fields_to_env_data(self.get_meta(env_data), env_data)
        obtained = [(field.name, value) for field, value in pairs]
        self.assertEqual(expected, obtained)

    def make_valid_pairs(self):
        """Create and return a list of valid (field name, value) pairs."""
        return [
            ('type', 'local'),
            ('name', 'lxc'),
            ('lxc-clone', False),
            ('lxc-clone-aufs', False),
            ('root-dir', '/my/juju/local/'),
            ('storage-port', 4242),
            ('shared-storage-port', 4747),
            ('network-bridge', 'lxcbr1'),
            ('admin-secret', 'Secret!'),
            ('default-series', 'saucy'),
            ('is-default', True),
        ]

    def test_valid_env_data(self):
        # The field/value pairs are correctly returned.
        expected = self.make_valid_pairs()
        env_data = dict(expected)
        self.assert_name_value_pairs(expected, env_data)

    def test_missing_pairs(self):
        # None values are returned if a defined field is missing in env_data.
        expected = [
            ('type', 'local'),
            ('name', 'lxc'),
            ('lxc-clone', None),
            ('lxc-clone-aufs', None),
            ('root-dir', None),
            ('storage-port', None),
            ('shared-storage-port', None),
            ('network-bridge', None),
            ('admin-secret', None),
            ('default-series', None),
            ('is-default', None),
        ]
        env_data = {'type': 'local', 'name': 'lxc'}
        self.assert_name_value_pairs(expected, env_data)

    def test_unexpected_pairs(self):
        # Additional unexpected field/value pairs are returned as well.
        expected_pairs = self.make_valid_pairs()
        unexpected_pairs = [
            ('registry', 'USS Enterprise (NCC-1701-D)'),
            ('class', 'Galaxy'),
            ('years-of-service', 8),
            ('crashed', True),
            ('cloaking-device', None),
        ]
        env_data = dict(expected_pairs + unexpected_pairs)
        pairs = envs.map_fields_to_env_data(self.get_meta(env_data), env_data)
        # The expected fields are correctly returned.
        mapped_pairs = [
            (field.name, value) for field, value in pairs[:len(expected_pairs)]
        ]
        self.assertEqual(expected_pairs, mapped_pairs)
        # Pairs also include the unexpected fields.
        unexpected_dict = dict(unexpected_pairs)
        remaining_pairs = pairs[len(expected_pairs):]
        self.assertEqual(len(unexpected_dict), len(remaining_pairs))
        help = 'this field is unrecognized and can be safely removed'
        for field, value in remaining_pairs:
            self.assertIsInstance(field, fields.UnexpectedField)
            self.assertEqual(unexpected_dict[field.name], value, field.name)
            self.assertFalse(field.required, field.name)
            self.assertEqual(help, field.help, field.name)


class ValidateNormalizeTestsMixin(object):
    """Shared utilities for tests exercising "validate" and "normalize"."""

    def setUp(self):
        # Set up metadata to work with.
        choices = ('trick', 'treat')
        self.env_metadata = {
            'fields': (
                fields.StringField('string-required', required=True),
                fields.StringField('string-default', default='boo!'),
                fields.IntField('int-optional'),
                fields.IntField('int-range', min_value=42, max_value=47),
                fields.BoolField('bool-true', default=True),
                fields.ChoiceField('choice-optional', choices=choices)
            )
        }
        super(ValidateNormalizeTestsMixin, self).setUp()


class TestValidate(ValidateNormalizeTestsMixin, unittest.TestCase):

    def test_valid(self):
        # An empty errors dict is returned if the env_data is valid.
        env_data = {
            'string-required': 'a string',
            'string-default': 'another string',
            'int-optional': -42,
            'int-range': 42,
            'bool-true': False,
            'choice-optional': 'treat',
        }
        self.assertEqual({}, envs.validate(self.env_metadata, env_data))

    def test_valid_only_required(self):
        # To be valid, env_data must at least include the required values.
        env_data = {'string-required': 'a string'}
        validation_errors = envs.validate(self.env_metadata, env_data)
        # No validation errors were found.
        self.assertEqual(validation_errors, {})

    def test_not_valid(self):
        # An errors dict is returned if the env_data is not valid.
        env_data = {
            'string-required': ' ',
            'string-default': 42,
            'int-optional': 'not-an-int',
            'int-range': 1000,
            'bool-true': [],
            'choice-optional': 'toy',
        }
        expected = {
            'string-required': (
                'a value is required for the string-required field'),
            'string-default': (
                'the string-default field requires a string value'),
            'int-optional': 'the int-optional field requires an integer value',
            'int-range': 'the int-range value must be in the 42-47 range',
            'bool-true': 'the bool-true field requires a boolean value',
            'choice-optional': ('the choice-optional requires the value to be '
                                'one of the following: trick, treat'),
        }
        self.assertEqual(expected, envs.validate(self.env_metadata, env_data))

    def test_required_field_not_found(self):
        # An error is returned if required fields are not included in env_data.
        expected = {
            'string-required': (
                'a value is required for the string-required field'),
        }
        self.assertEqual(expected, envs.validate(self.env_metadata, {}))

    def test_optional_invalid_field(self):
        # Even if there is just one invalid field, and even if that field is
        # optional, the error is still reported in the errors dict.
        env_data = {
            'string-required': 'a string',
            'int-optional': False,
        }
        expected = {
            'int-optional': 'the int-optional field requires an integer value',
        }
        self.assertEqual(expected, envs.validate(self.env_metadata, env_data))


class TestNormalize(ValidateNormalizeTestsMixin, unittest.TestCase):

    def test_normalized_data(self):
        # The given env_data is properly normalized.
        env_data = {
            'string-required': ' a string\n',
            'string-default': '\t another one',
            'int-optional': '-42',
            'int-range': 42.2,
            'bool-true': False,
            'choice-optional': ' trick ',
        }
        expected = {
            'string-required': 'a string',
            'string-default': 'another one',
            'int-optional': -42,
            'int-range': 42,
            'bool-true': False,
            'choice-optional': 'trick',
        }
        self.assertEqual(expected, envs.normalize(self.env_metadata, env_data))

    def test_already_normalized(self):
        # The normalization process produces the same env_data if the input
        # data is already normalized.
        env_data = {
            'string-required': 'a string',
            'int-optional': 42,
        }
        normalized_data = envs.normalize(self.env_metadata, env_data)
        # The same data is returned.
        self.assertEqual(env_data, normalized_data)
        # However, the returned data is a different object.
        self.assertIsNot(env_data, normalized_data)

    def test_multiline_values_preserved(self):
        # The normalization process preserves multi-line values.
        env_data = {'string-required': 'first line\nsecond line'}
        normalized_data = envs.normalize(self.env_metadata, env_data)
        self.assertEqual(env_data, normalized_data)

    def test_exclude_fields(self):
        # The normalization process excludes fields if they are not required
        # and the corresponding values are not set or not changed.
        env_data = {
            # Since this field is required, it is included even if not set.
            'string-required': '',
            # Even if this value is the default one, it is included because
            # it is explicitly set by the user.
            'string-default': 'boo!',
            # Since this field has a value, it is included even if optional.
            'int-optional': 42,
            # Since the value is unset and the field optional, it is excluded.
            'int-range': None,
            # False is a valid set value for boolean fields. For this reason,
            # it is included.
            'bool-true': False,
            # The choice optional field is not in the input data. For this
            # reason the field is excluded.
        }
        expected = {
            'string-required': None,
            'string-default': 'boo!',
            'int-optional': 42,
            'bool-true': False,
        }
        normalized_data = envs.normalize(self.env_metadata, env_data)
        self.assertEqual(expected, normalized_data)

    def test_exclude_unexpected_fields(self):
        # The normalization process excludes unexpected fields if the
        # corresponding values are not set.
        env_data = {
            # Since this field is required, it is included even if not set.
            'string-required': 'a string',
            # Since the value is set, this value is preserved even if the
            # field is not included in metadata.
            'unexpected1': 'boo!',
            # False is also considered a valid value for an unexpected field.
            'unexpected2': False,
            # Unexpected fields whose value is empty or None are excluded.
            'unexpected3': '',
            'unexpected4': '\t\n ',
            'unexpected5': None,
        }
        expected = {
            'string-required': 'a string',
            'unexpected1': 'boo!',
            'unexpected2': False,
        }
        normalized_data = envs.normalize(self.env_metadata, env_data)
        self.assertEqual(expected, normalized_data)

    def test_original_not_mutated(self):
        # The original env_data is not modified in the process.
        env_data = {
            'string-required': ' a string\n',
            'string-default': None,
            'bool-true': None,
            'choice-optional': ' trick ',
        }
        original = env_data.copy()
        expected = {
            'string-required': 'a string',
            'choice-optional': 'trick',
        }
        normalized_data = envs.normalize(self.env_metadata, env_data)
        self.assertEqual(expected, normalized_data)
        self.assertEqual(original, env_data)


class TestGetEnvShortDescription(unittest.TestCase):

    def test_env(self):
        # The env description includes the environment name and type.
        env_data = {'name': 'lxc', 'type': 'local', 'is-default': False}
        description = envs.get_env_short_description(env_data)
        self.assertEqual('lxc (type: local)', description)

    def test_default_env(self):
        # A default environment is properly described.
        env_data = {'name': 'lxc', 'type': 'local', 'is-default': True}
        description = envs.get_env_short_description(env_data)
        self.assertEqual('lxc (type: local, default)', description)

    def test_env_without_type(self):
        # Without the type we can only show the environment name.
        env_data = {'name': 'lxc', 'is-default': False}
        description = envs.get_env_short_description(env_data)
        self.assertEqual('lxc', description)

    def test_default_env_without_type(self):
        # This would be embarrassing.
        env_data = {'name': 'lxc', 'type': None, 'is-default': True}
        description = envs.get_env_short_description(env_data)
        self.assertEqual('lxc (default)', description)
