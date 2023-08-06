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

"""Tests for the Juju Quickstart management infrastructure."""

from __future__ import unicode_literals

import argparse
from contextlib import contextmanager
import logging
import os
import shutil
import StringIO as io
import unittest

import mock
import yaml

import quickstart
from quickstart import (
    manage,
    settings,
)
from quickstart.cli import (
    params,
    views,
)
from quickstart.models import (
    bundles,
    envs,
    jenv,
    references,
)
from quickstart.tests import helpers


class TestDescriptionAction(unittest.TestCase):

    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            '--test', action=manage._DescriptionAction, nargs=0)

    @mock.patch('sys.exit')
    @helpers.mock_print
    def test_action(self, mock_print, mock_exit):
        # The action just prints the description and exits.
        args = self.parser.parse_args(['--test'])
        self.assertIsNone(args.test)
        mock_print.assert_called_once_with(settings.DESCRIPTION)
        mock_exit.assert_called_once_with(0)


class TestGetPackagingInfo(unittest.TestCase):

    distro_only_disable = '(enabled by default, use --ppa to disable)'
    ppa_disable = '(enabled by default, use --distro-only to disable)'

    def test_ppa_source_apt(self):
        # The returned distro_only flag is set to False and the help texts are
        # formatted accordingly when the passed Juju source is "ppa".
        distro_only, distro_only_help, ppa_help = manage._get_packaging_info(
            'ppa', platform=settings.LINUX_APT)
        self.assertFalse(distro_only)
        self.assertNotIn(self.distro_only_disable, distro_only_help)
        self.assertIn(self.ppa_disable, ppa_help)

    def test_distro_source_apt(self):
        # The returned distro_only flag is set to True and the help texts are
        # formatted accordingly when the passed Juju source is "distro".
        distro_only, distro_only_help, ppa_help = manage._get_packaging_info(
            'distro', platform=settings.LINUX_APT)
        self.assertTrue(distro_only)
        self.assertIn(self.distro_only_disable, distro_only_help)
        self.assertNotIn(self.ppa_disable, ppa_help)

    def test_not_apt(self):
        # If the platform is not LINUX_APT then distro_only should be False
        # and the help is suppressed.
        for platform in (settings.LINUX_RPM, settings.WINDOWS, settings.OSX):
            distro_only, dist_only_help, ppa_help = manage._get_packaging_info(
                'dontcare', platform=platform)
            self.assertTrue(distro_only)
            self.assertEqual(argparse.SUPPRESS, dist_only_help)
            self.assertEqual(argparse.SUPPRESS, ppa_help)


class TestValidateCharmUrl(unittest.TestCase):

    def setUp(self):
        self.parser = mock.Mock()

    def make_options(self, charm_url, has_bundle=False):
        """Return a mock options object which includes the passed arguments."""
        options = mock.Mock(charm_url=charm_url, bundle_source=None)
        if has_bundle:
            options.bundle_source = 'u/who/django/42'
        return options

    def test_invalid_url_error(self):
        # A parser error is invoked if the charm URL is not valid.
        options = self.make_options('cs:invalid')
        manage._validate_charm_url(options, self.parser)
        expected = 'URL has invalid form: cs:invalid'
        self.parser.error.assert_called_once_with(expected)

    def test_local_charm_error(self):
        # A parser error is invoked if a local charm is provided.
        options = self.make_options('local:precise/juju-gui-100')
        manage._validate_charm_url(options, self.parser)
        expected = 'local charms are not allowed: local:precise/juju-gui-100'
        self.parser.error.assert_called_once_with(expected)

    def test_unsupported_series_error(self):
        # A parser error is invoked if the charm series is not supported.
        options = self.make_options('cs:nosuch/juju-gui-100')
        manage._validate_charm_url(options, self.parser)
        expected = 'unsupported charm series: nosuch'
        self.parser.error.assert_called_once_with(expected)

    def test_outdated_charm_error(self):
        # A parser error is invoked if a bundle deployment has been requested
        # but the provided charm does not support bundles.
        options = self.make_options('cs:precise/juju-gui-1', has_bundle=True)
        manage._validate_charm_url(options, self.parser)
        expected = (
            'bundle deployments not supported by the requested charm '
            'revision: cs:precise/juju-gui-1')
        self.parser.error.assert_called_once_with(expected)

    def test_outdated_allowed_without_bundles(self):
        # An outdated charm is allowed if no bundles are provided.
        options = self.make_options('cs:precise/juju-gui-1', has_bundle=False)
        manage._validate_charm_url(options, self.parser)
        self.assertFalse(self.parser.error.called)

    def test_success(self):
        # The functions completes without error if the charm URL is valid.
        good = (
            'cs:precise/juju-gui-100',
            'cs:~juju-gui/precise/juju-gui-42',
            'cs:~who/precise/juju-gui-42',
            'cs:~who/precise/my-juju-gui-42',
        )
        for charm_url in good:
            options = self.make_options(charm_url)
            manage._validate_charm_url(options, self.parser)
            self.assertFalse(self.parser.error.called, charm_url)


class TestRetrieveEnvDb(helpers.EnvFileTestsMixin, unittest.TestCase):

    def setUp(self):
        self.parser = mock.Mock()

    def test_existing_env_file(self):
        # The env_db is correctly retrieved from an existing environments file.
        env_file = self.make_env_file()
        env_db = manage._retrieve_env_db(self.parser, env_file=env_file)
        self.assertEqual(yaml.safe_load(self.valid_contents), env_db)

    def test_error_parsing_env_file(self):
        # A parser error is invoked if an error occurs parsing the env file.
        env_file = self.make_env_file('so-bad')
        manage._retrieve_env_db(self.parser, env_file=env_file)
        self.parser.error.assert_called_once_with(
            'invalid YAML contents in {}: so-bad'.format(env_file))

    def test_missing_env_file(self):
        # An empty env_db is returned if the environments file does not exist.
        env_db = manage._retrieve_env_db(self.parser, env_file=None)
        self.assertEqual(envs.create_empty_env_db(), env_db)


@mock.patch('quickstart.manage.envs.save')
class TestCreateSaveCallable(unittest.TestCase):

    def setUp(self):
        self.parser = mock.Mock()
        self.env_file = '/tmp/envfile.yaml'
        self.env_db = helpers.make_env_db()
        with mock.patch('quickstart.manage.utils.run_once') as mock_run_once:
            self.save_callable = manage._create_save_callable(
                self.parser, self.env_file)
        self.mock_run_once = mock_run_once

    def test_saved(self, mock_save):
        # The returned function correctly saves the new environments database.
        self.save_callable(self.env_db)
        mock_save.assert_called_once_with(
            self.env_file, self.env_db, backup_function=self.mock_run_once())
        self.assertFalse(self.parser.error.called)

    def test_error(self, mock_save):
        # The returned function uses the parser to exit the program if an error
        # occurs while saving the new environments database.
        mock_save.side_effect = OSError(b'bad wolf')
        self.save_callable(self.env_db)
        mock_save.assert_called_once_with(
            self.env_file, self.env_db, backup_function=self.mock_run_once())
        self.parser.error.assert_called_once_with('bad wolf')

    def test_backup_function(self, mock_save):
        # The backup function is correctly created.
        self.save_callable(self.env_db)
        self.mock_run_once.assert_called_once_with(shutil.copyfile)


class TestStartInteractiveSession(
        helpers.EnvFileTestsMixin, unittest.TestCase):

    def setUp(self):
        # Set up a parser, the environments metadata, an environments file and
        # a testing env_db.
        self.parser = mock.Mock()
        self.env_type_db = envs.get_env_type_db()
        self.env_file = self.make_env_file()
        self.env_db = envs.load(self.env_file)
        self.jenv_db = helpers.make_jenv_db()

    @contextmanager
    def patch_interactive_mode(self, env_db, jenv_db, return_value):
        """Patch the quickstart.cli.views.show function.

        Ensure the interactive mode is started by the code in the context block
        passing the given env_db and jenv_db.
        Make the view return the given return_value.
        """
        create_save_callable_path = 'quickstart.manage._create_save_callable'
        mock_show = mock.Mock(return_value=return_value)
        with mock.patch(create_save_callable_path) as mock_save_callable:
            with mock.patch('quickstart.manage.views.show', mock_show):
                yield
        mock_save_callable.assert_called_once_with(self.parser, self.env_file)
        expected_params = params.Params(
            env_type_db=self.env_type_db,
            env_db=env_db,
            jenv_db=jenv_db,
            save_callable=mock_save_callable(),
            remove_jenv_callable=jenv.remove,
        )
        mock_show.assert_called_once_with(views.env_index, expected_params)

    def test_resulting_env_data(self):
        # The interactive session can be used to select an environment, in
        # which case the function returns the corresponding env_data.
        env_data = envs.get_env_data(self.env_db, 'aws')
        with self.patch_interactive_mode(
                self.env_db, self.jenv_db, [self.env_db, env_data]):
            obtained_env_data = manage._start_interactive_session(
                self.parser, self.env_type_db, self.env_db, self.jenv_db,
                self.env_file)
        self.assertEqual(env_data, obtained_env_data)

    @helpers.mock_print
    def test_modified_environments(self, mock_print):
        # The function informs the user that environments have been modified
        # during the interactive session.
        env_data = envs.get_env_data(self.env_db, 'aws')
        new_env_db = helpers.make_env_db()
        with self.patch_interactive_mode(
                self.env_db, self.jenv_db, [new_env_db, env_data]):
            manage._start_interactive_session(
                self.parser, self.env_type_db, self.env_db, self.jenv_db,
                self.env_file)
        mock_print.assert_called_once_with(
            'changes to the environments file have been saved')

    @mock.patch('sys.exit')
    def test_interactive_mode_quit(self, mock_exit):
        # If the user explicitly quits the interactive mode, the program exits
        # without proceeding with the environment bootstrapping.
        with self.patch_interactive_mode(
                self.env_db, self.jenv_db, [self.env_db, None]):
            manage._start_interactive_session(
                self.parser, self.env_type_db, self.env_db, self.jenv_db,
                self.env_file)
        mock_exit.assert_called_once_with('quitting')


class TestRetrieveEnvData(unittest.TestCase):

    def setUp(self):
        # Set up a parser, the environments metadata and a testing env_db.
        self.parser = mock.Mock()
        self.env_type_db = envs.get_env_type_db()
        self.env_db = helpers.make_env_db()
        self.jenv_db = helpers.make_jenv_db()

    def test_resulting_env_data(self):
        # The env_data is correctly validated and returned.
        expected_env_data = envs.get_env_data(self.env_db, 'lxc')
        env_data = manage._retrieve_env_data(
            self.parser, self.env_type_db, self.env_db, self.jenv_db, 'lxc')
        self.assertEqual(expected_env_data, env_data)

    def test_jenv_data(self):
        # The env_data is correctly retrieved from the jenv database.
        expected_env_data = envs.get_env_data(self.jenv_db, 'test-jenv')
        env_data = manage._retrieve_env_data(
            self.parser, self.env_type_db, self.env_db, self.jenv_db,
            'test-jenv')
        self.assertEqual(expected_env_data, env_data)

    def test_error_environment_not_found(self):
        # A parser error is invoked if the provided environment is not included
        # in the environments database.
        manage._retrieve_env_data(
            self.parser, self.env_type_db, self.env_db, self.jenv_db,
            'no-such')
        self.parser.error.assert_called_once_with(
            'environment no-such not found')

    def test_error_environment_not_valid(self):
        # A parser error is invoked if the selected environment is not valid.
        manage._retrieve_env_data(
            self.parser, self.env_type_db, self.env_db, self.jenv_db,
            'local-with-errors')
        self.parser.error.assert_called_once_with(
            'cannot use the local-with-errors environment:\n'
            'the storage port field requires an integer value')


class TestValidatePlatform(unittest.TestCase):

    def setUp(self):
        # Set up a parser, the environments metadata and a testing env_db.
        self.parser = mock.Mock()
        self.env_type_db = envs.get_env_type_db()
        self.env_db = helpers.make_env_db()

    def test_platform_validation_fails(self):
        # If the platform validation fails a parser error is given.
        path = 'quickstart.manage.platform_support.validate_platform'
        with mock.patch(path, side_effect=ValueError('Bad platform, yo')):
            manage._validate_platform(self.parser, settings.LINUX_RPM)
        self.parser.error.assert_called_once_with(
            'Bad platform, yo')

    def test_platform_validation_passes(self):
        # If the platform validation passes it returns None.
        path = 'quickstart.platform_support.validate_platform'
        with mock.patch(path, side_effect=None):
            result = manage._validate_platform(self.parser, settings.LINUX_RPM)
        self.assertIsNone(result)


class TestSetupEnv(
        helpers.EnvFileTestsMixin, helpers.JenvFileTestsMixin,
        unittest.TestCase):

    def setUp(self):
        self.parser = mock.Mock()

    def make_options(self, env_file, env_name=None, interactive=False,
                     platform=settings.LINUX_APT):
        """Return a mock options object which includes the passed arguments."""
        return mock.Mock(
            env_file=env_file,
            env_name=env_name,
            interactive=interactive,
            platform=platform,
        )

    def patch_interactive_mode(self, return_value):
        """Patch the quickstart.manage._start_interactive_session function.

        Make the mocked function return the given return_value.
        """
        mock_start_interactive_session = mock.Mock(return_value=return_value)
        return mock.patch(
            'quickstart.manage._start_interactive_session',
            mock_start_interactive_session)

    def test_resulting_options(self):
        # The options object is correctly set up.
        env_file = self.make_env_file()
        options = self.make_options(
            env_file, env_name='aws', interactive=False)
        manage._setup_env(options, self.parser)
        self.assertEqual(env_file, options.env_file)
        self.assertEqual('aws', options.env_name)
        self.assertEqual('ec2', options.env_type)
        self.assertEqual('saucy', options.default_series)
        self.assertFalse(options.interactive)

    def test_expand_user(self):
        # The ~ construct is correctly expanded in the validation process.
        env_file = self.make_env_file()
        # Split the full path of the env file, e.g. from a full "/tmp/env.file"
        # path retrieve the base path "/tmp" and the file name "env.file".
        # By doing that we can simulate that the user's home is "/tmp" and that
        # the env file is "~/env.file".
        base_path, filename = os.path.split(env_file)
        path = '~/{}'.format(filename)
        options = self.make_options(env_file=path, env_name='aws')
        with mock.patch('os.environ', {'HOME': base_path}):
            manage._setup_env(options, self.parser)
        self.assertEqual(env_file, options.env_file)

    def test_no_env_name(self):
        # A parser error is invoked if the environment name is missing and
        # interactive mode is disabled.
        options = self.make_options(self.make_env_file(), interactive=False)
        manage._setup_env(options, self.parser)
        self.assertTrue(self.parser.error.called)
        message = self.parser.error.call_args[0][0]
        self.assertIn('unable to find an environment name to use', message)

    def test_local_provider_linux(self):
        # Local environments are correctly handled.
        contents = yaml.safe_dump({
            'environments': {
                'lxc': {'admin-secret': 'Secret!', 'type': 'local'},
            },
        })
        env_file = self.make_env_file(contents)
        options = self.make_options(
            env_file, env_name='lxc', interactive=False)
        manage._setup_env(options, self.parser)
        self.assertEqual(env_file, options.env_file)
        self.assertEqual('lxc', options.env_name)
        self.assertEqual('local', options.env_type)
        self.assertIsNone(options.default_series)
        self.assertFalse(options.interactive)

    def test_local_provider_not_linux(self):
        # Local environments are correctly handled.
        contents = yaml.safe_dump({
            'environments': {
                'lxc': {'admin-secret': 'Secret!', 'type': 'local'},
            },
        })
        env_file = self.make_env_file(contents)
        options = self.make_options(
            env_file, env_name='lxc', interactive=False,
            platform=settings.OSX)
        manage._setup_env(options, self.parser)
        self.assertTrue(self.parser.error.called)
        message = self.parser.error.call_args[0][0]
        self.assertEqual(
            'this host platform does not support local environments',
            message)

    def test_interactive_mode(self):
        # The interactive mode is started properly if the corresponding option
        # flag is set.
        env_file = self.make_env_file()
        options = self.make_options(env_file, interactive=True)
        # Simulate the user did not make any changes to the env_db from the
        # interactive session.
        env_db = yaml.load(self.valid_contents)
        # Simulate the aws environment has been selected and started from the
        # interactive session.
        env_data = envs.get_env_data(env_db, 'aws')
        get_env_type_db_path = 'quickstart.models.envs.get_env_type_db'
        with mock.patch(get_env_type_db_path) as mock_get_env_type_db:
            with self.make_jenv('ec2', yaml.safe_dump(self.jenv_data)):
                jenv_db = jenv.get_env_db()
                with self.patch_interactive_mode(env_data) as mock_interactive:
                    manage._setup_env(options, self.parser)
        mock_interactive.assert_called_once_with(
            self.parser, mock_get_env_type_db(), env_db, jenv_db, env_file)
        # The options is updated with data from the selected environment.
        self.assertEqual(env_file, options.env_file)
        self.assertEqual('aws', options.env_name)
        self.assertEqual('ec2', options.env_type)
        self.assertEqual('saucy', options.default_series)
        self.assertTrue(options.interactive)

    @helpers.mock_print
    def test_missing_env_file(self, mock_print):
        # If the environments file does not exist, an empty env_db is created
        # in memory and interactive mode is forced.
        new_env_db = helpers.make_env_db()
        env_data = envs.get_env_data(new_env_db, 'lxc')
        options = self.make_options('__no_such_env_file__', interactive=False)
        # In this case, we expect the interactive mode to be started and the
        # env_db passed to the view to be an empty one.
        with self.patch_interactive_mode(env_data) as mock_interactive:
            manage._setup_env(options, self.parser)
        self.assertTrue(mock_interactive.called)
        self.assertTrue(options.interactive)


class TestConvertOptionsToUnicode(unittest.TestCase):

    def test_bytes_options(self):
        # Byte strings are correctly converted.
        options = argparse.Namespace(opt1=b'val1', opt2=b'val2')
        manage._convert_options_to_unicode(options)
        self.assertEqual('val1', options.opt1)
        self.assertIsInstance(options.opt1, unicode)
        self.assertEqual('val2', options.opt2)
        self.assertIsInstance(options.opt2, unicode)

    def test_unicode_options(self):
        # Unicode options are left untouched.
        options = argparse.Namespace(myopt='myval')
        self.assertEqual('myval', options.myopt)
        self.assertIsInstance(options.myopt, unicode)

    def test_other_types(self):
        # Other non-string types are left untouched.
        options = argparse.Namespace(opt1=42, opt2=None)
        self.assertEqual(42, options.opt1)
        self.assertIsNone(options.opt2)


@mock.patch('quickstart.manage._setup_env', mock.Mock())
class TestSetup(unittest.TestCase):

    def patch_get_default_env_name(self, env_name=None):
        """Patch the function used by setup() to retrieve the default env name.

        This way the test does not rely on the user's Juju environment set up,
        and it is also possible to simulate an arbitrary environment name.
        """
        mock_get_default_env_name = mock.Mock(return_value=env_name)
        path = 'quickstart.manage.envs.get_default_env_name'
        return mock.patch(path, mock_get_default_env_name)

    def call_setup(self, args, env_name='ec2', exit_called=True):
        """Call the setup function simulating the given args and env name.

        Also ensure the program exits without errors if exit_called is True.
        """
        with mock.patch('sys.argv', ['juju-quickstart'] + args):
            with mock.patch('sys.exit') as mock_exit:
                with self.patch_get_default_env_name(env_name):
                    options = manage.setup()
        if exit_called:
            mock_exit.assert_called_once_with(0)
        return options

    def test_help(self):
        # The program help message is properly formatted.
        with mock.patch('sys.stdout') as mock_stdout:
            self.call_setup(['--help'])
        stdout_write = mock_stdout.write
        self.assertTrue(stdout_write.called)
        # Retrieve the output from the mock call.
        output = stdout_write.call_args[0][0]
        self.assertIn('usage: juju-quickstart', output)
        # NB: some shells break the docstring at different places when --help
        # is called so the replacements below make it agnostic.
        self.assertIn(quickstart.__doc__.replace('\n', ' '),
                      output.replace('\n', ' '))
        self.assertIn('--environment', output)
        # Without a default environment, the -e option has no default.
        self.assertIn('The name of the Juju environment to use (ec2)\n',
                      output)

    def test_help_with_default_environment(self):
        # The program help message is properly formatted when a default Juju
        # environment is found.
        with mock.patch('sys.stdout') as mock_stdout:
            self.call_setup(['--help'], env_name='hp')
        stdout_write = mock_stdout.write
        self.assertTrue(stdout_write.called)
        # Retrieve the output from the mock call.
        output = stdout_write.call_args[0][0]
        self.assertIn('The name of the Juju environment to use (hp)\n', output)

    def test_description(self):
        # The program description is properly printed out as required by juju.
        with helpers.mock_print as mock_print:
            self.call_setup(['--description'])
        mock_print.assert_called_once_with(settings.DESCRIPTION)

    def test_version(self):
        # The program version is properly printed to stderr.
        with mock.patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
            self.call_setup(['--version'])
        expected = 'juju-quickstart {}\n'.format(quickstart.get_version())
        self.assertEqual(expected, mock_stderr.getvalue())

    @mock.patch('quickstart.models.bundles.from_source')
    def test_bundle(self, mock_from_source):
        # The bundle validation process is started if a bundle is provided.
        self.call_setup(['/path/to/bundle.yaml'], exit_called=False)
        mock_from_source.assert_called_once_with('/path/to/bundle.yaml', None)

    def test_bundle_error(self):
        # The bundle validation process fails if an invalid bundle source is
        # provided.
        with mock.patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
            self.call_setup(['invalid/bundle!'], exit_called=False)
        expected_error = (
            'error: unable to open the bundle: invalid bundle URL: '
            'invalid/bundle!')
        self.assertIn(expected_error, mock_stderr.getvalue())

    @mock.patch('quickstart.manage._validate_charm_url')
    def test_charm_url(self, mock_validate_charm_url):
        # The charm URL validation process is started if a URL is provided.
        self.call_setup(
            ['--gui-charm-url', 'cs:precise/juju-gui-42'], exit_called=False)
        self.assertTrue(mock_validate_charm_url.called)
        options, parser = mock_validate_charm_url.call_args_list[0][0]
        self.assertIsInstance(options, argparse.Namespace)
        self.assertIsInstance(parser, argparse.ArgumentParser)

    def test_configure_logging(self):
        # Logging is properly set up at the info level.
        logger = logging.getLogger()
        self.call_setup([], 'ec2', exit_called=False)
        self.assertEqual(logging.INFO, logger.level)

    def test_configure_logging_debug(self):
        # Logging is properly set up at the debug level.
        logger = logging.getLogger()
        self.call_setup(['--debug'], 'ec2', exit_called=False)
        self.assertTrue(logging.DEBUG, logger.level)

    def test_upload_tools(self):
        # Upload tools is properly set up.
        options = self.call_setup(['--upload-tools'], exit_called=False)
        self.assertTrue(options.upload_tools)


@mock.patch('webbrowser.open')
@mock.patch('quickstart.manage.app')
@mock.patch('__builtin__.print', mock.Mock())
class TestRun(helpers.BundleFileTestsMixin, unittest.TestCase):

    juju_command = '/sbin/juju'

    def make_options(self, **kwargs):
        """Set up the options to be passed to the run function."""
        options = {
            'bundle_source': None,
            'charm_url': None,
            'debug': False,
            'env_name': 'aws',
            'env_type': 'ec2',
            'open_browser': True,
            'default_series': None,
        }
        options.update(kwargs)
        return mock.Mock(**options)

    def configure_app(self, mock_app, **kwargs):
        """Configure the given mock_app with the given kwargs.

        Each key/value pair in kwargs represents a mock_app attribute and
        the associated return value. Those values are used to override
        defaults.

        Return the mock Juju environment object.
        """
        env = mock.Mock()
        defaults = {
            # Dependencies are installed.
            'ensure_dependencies': (1, 22, 0),
            # Ensure the current Juju version is supported.
            'check_juju_supported': None,
            # Ensure the SSH keys are properly configured.
            'ensure_ssh_keys': None,
            # The environment is not already bootstrapped.
            'check_bootstrapped': None,
            # This is also confirmed by the bootstrap function.
            'bootstrap': False,
            # Status is then called, returning the bootstrap node series.
            'status': 'trusty',
            # The API address must be retrieved (the environment is not ready).
            'get_api_address': '1.2.3.4:17070',
            # Retrieve the environment unique identifier.
            'get_env_uuid_or_none': 'env-uuid',
            # Retrieve the environment credentials.
            'get_credentials': ('MyUser', 'Secret!'),
            # Connect to the Juju Environment API endpoint.
            'connect': env,
            # The environment is then checked.
            'check_environment': (
                references.Reference.from_fully_qualified_url(
                    'cs:trusty/juju-gui-42'),
                '0',
                {'Name': 'juju-gui'},
                {'Name': 'juju-gui/0'}
            ),
            # Deploy the Juju GUI charm.
            'deploy_gui': 'juju-gui/0',
            # Watch the deployment progress and return the unit address.
            'watch': '1.2.3.5',
            # Create the login token for the Juju GUI.
            'create_auth_token': 'TOKEN',
        }
        defaults.update(kwargs)
        for attr, return_value in defaults.items():
            getattr(mock_app, attr).return_value = return_value
        return env

    def patch_get_juju_command(self):
        """Patch the platform_support.get_juju_command function."""
        path = 'quickstart.manage.platform_support.get_juju_command'
        return mock.patch(path, return_value=(self.juju_command, False))

    def test_run(self, mock_app, mock_open):
        # The application runs correctly if no bundle is provided.
        env = self.configure_app(mock_app)
        # Run the application.
        options = self.make_options()
        with self.patch_get_juju_command():
            manage.run(options)
        # Ensure the functions have been used correctly.
        mock_app.ensure_dependencies.assert_called_once_with(
            options.distro_only, options.platform, self.juju_command)
        mock_app.check_juju_supported.assert_called_once_with((1, 22, 0))
        mock_app.ensure_ssh_keys.assert_called_once_with()
        mock_app.check_bootstrapped.assert_called_once_with(options.env_name)
        mock_app.bootstrap.assert_called_once_with(
            options.env_name, self.juju_command,
            debug=options.debug,
            upload_tools=options.upload_tools,
            upload_series=options.upload_series,
            constraints=options.constraints)
        mock_app.status.assert_called_once_with(
            options.env_name, self.juju_command)
        mock_app.get_api_address.assert_called_once_with(
            options.env_name, self.juju_command)
        mock_app.get_env_uuid_or_none.assert_called_once_with(options.env_name)
        mock_app.get_credentials.assert_called_once_with(options.env_name)
        mock_app.connect.assert_has_calls([
            mock.call(
                'wss://1.2.3.4:17070/environment/env-uuid/api',
                'MyUser',
                'Secret!'),
            mock.call().close(),
            mock.call(
                'wss://1.2.3.5:443/ws/environment/env-uuid/api',
                'MyUser',
                'Secret!'),
            mock.call().close(),
        ])
        mock_app.check_environment.assert_called_once_with(
            env, settings.JUJU_GUI_SERVICE_NAME, options.charm_url,
            options.env_type, 'trusty', False)
        mock_app.deploy_gui.assert_called_once_with(
            env, settings.JUJU_GUI_SERVICE_NAME, 'cs:trusty/juju-gui-42',
            '0', {'Name': 'juju-gui'}, {'Name': 'juju-gui/0'})
        mock_app.watch.assert_called_once_with(env, 'juju-gui/0')
        mock_app.create_auth_token.assert_called_once_with(env)
        mock_open.assert_called_once_with('https://1.2.3.5/?authtoken=TOKEN')
        # Ensure some of the app function have not been called.
        self.assertFalse(mock_app.get_env_type.called)
        self.assertFalse(mock_app.deploy_bundle.called)

    def test_old_juju_api_endpoint(self, mock_app, mock_open):
        # The old Juju WebSocket API endpoint is used if the Juju version is
        # not recent enough.
        self.configure_app(mock_app, ensure_dependencies=(1, 19, 0))
        # Run the application.
        options = self.make_options()
        with self.patch_get_juju_command():
            manage.run(options)
        mock_app.connect.assert_has_calls([
            mock.call('wss://1.2.3.4:17070', 'MyUser', 'Secret!'),
            mock.call().close(),
            mock.call('wss://1.2.3.5:443/ws', 'MyUser', 'Secret!'),
            mock.call().close(),
        ])

    def test_new_api_endpoint_old_charm(self, mock_app, mock_open):
        # Even if the Juju version is new, the old GUI server login API is used
        # if the charm in the environment is not recent enough.
        self.configure_app(mock_app, check_environment=(
            references.Reference.from_fully_qualified_url(
                'cs:trusty/juju-gui-0'),
            '0',
            {'Name': 'juju-gui'},
            {'Name': 'juju-gui/0'}
        ))
        # Run the application.
        options = self.make_options()
        with self.patch_get_juju_command():
            manage.run(options)
        mock_app.connect.assert_has_calls([
            mock.call(
                'wss://1.2.3.4:17070/environment/env-uuid/api',
                'MyUser',
                'Secret!'),
            mock.call().close(),
            mock.call('wss://1.2.3.5:443/ws', 'MyUser', 'Secret!'),
            mock.call().close(),
        ])

    def test_already_bootstrapped(self, mock_app, mock_open):
        # The application correctly reuses an already bootstrapped environment.
        env = self.configure_app(mock_app, check_bootstrapped='example.com')
        # Run the application.
        options = self.make_options()
        with self.patch_get_juju_command():
            manage.run(options)
        # The environment type is retrieved from the jenv.
        mock_app.get_env_type.assert_called_once_with(env)
        # No reason to call bootstrap or get_api_address functions.
        self.assertFalse(mock_app.bootstrap.called)
        self.assertFalse(mock_app.get_api_address.called)

    def test_already_bootstrapped_race(self, mock_app, mock_open):
        # The application correctly reuses an already bootstrapped environment.
        # In this case, the environment seems not bootstrapped at first, but
        # it ended up being up and running later.
        env = self.configure_app(mock_app, bootstrap=True)
        # Run the application.
        options = self.make_options()
        with self.patch_get_juju_command():
            manage.run(options)
        # The bootstrap and get_api_address functions are still called, but
        # this time also get_env_type is required.
        # The environment type is retrieved from the jenv.
        mock_app.bootstrap.assert_called_once_with(
            options.env_name, self.juju_command,
            debug=options.debug,
            upload_tools=options.upload_tools,
            upload_series=options.upload_series,
            constraints=options.constraints)
        mock_app.get_api_address.assert_called_once_with(
            options.env_name, self.juju_command)
        mock_app.get_env_type.assert_called_once_with(env)

    def test_no_token(self, mock_app, mock_open):
        # The process continues even if the authentication token cannot be
        # retrieved.
        env = self.configure_app(mock_app, create_auth_token=None)
        # Run the application.
        options = self.make_options()
        with self.patch_get_juju_command():
            manage.run(options)
        # Ensure the browser is still open without an auth token.
        mock_app.create_auth_token.assert_called_once_with(env)
        mock_open.assert_called_once_with('https://1.2.3.5')

    def test_bundle(self, mock_app, mock_open):
        # A bundle is correctly deployed by the application.
        env = self.configure_app(mock_app, create_auth_token=None)
        bundle_source = 'mediawiki-single'
        reference = references.Reference.from_jujucharms_url(bundle_source)
        bundle = bundles.Bundle(self.bundle_data, reference=reference)
        # Run the application.
        options = self.make_options(bundle_source=bundle_source, bundle=bundle)
        with self.patch_get_juju_command():
            manage.run(options)
        # Ensure the bundle is correctly deployed.
        mock_app.deploy_bundle.assert_called_once_with(env, bundle)

    def test_local_provider(self, mock_app, mock_open):
        # The application correctly handles working with local providers with
        # new Juju versions not requiring "sudo" to bootstrap the environment.
        self.configure_app(mock_app, create_auth_token=None)
        # Run the application.
        options = self.make_options(env_type='local')
        with self.patch_get_juju_command():
            manage.run(options)

    def test_no_browser(self, mock_app, mock_open):
        # It is possible to avoid opening the GUI in the browser.
        self.configure_app(mock_app, create_auth_token=None)
        # Run the application.
        options = self.make_options(open_browser=False)
        with self.patch_get_juju_command():
            manage.run(options)
        # The browser is not opened.
        self.assertFalse(mock_open.called)
