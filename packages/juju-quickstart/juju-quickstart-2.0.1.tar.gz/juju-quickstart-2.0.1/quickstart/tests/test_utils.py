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

"""Tests for the Juju Quickstart utility functions and classes."""

from __future__ import unicode_literals

import datetime
import os
import shutil
import tempfile
import unittest

import mock

from quickstart import (
    get_version,
    utils,
)
from quickstart.tests import helpers


@helpers.mock_print
class TestAddAptRepository(helpers.CallTestsMixin, unittest.TestCase):

    apt_add_repository = '/usr/bin/add-apt-repository'
    apt_get = '/usr/bin/apt-get'
    repository = 'ppa:good/stuff'
    side_effects = (
        (0, 'first update', ''),  # Update the global repository.
        (0, 'apt-get install', ''),  # Install add-apt-repository.
        (0, 'add-apt-repository', ''),  # Add the repository.
        (0, 'second update', ''),  # Update the global repository.
    )

    def patch_codename(self, codename):
        """Patch the Ubuntu codename returned by get_ubuntu_codename."""
        return mock.patch(
            'quickstart.utils.get_ubuntu_codename',
            mock.Mock(return_value=codename))

    def test_precise(self, mock_print):
        # The repository is properly added in precise.
        with self.patch_codename('precise') as mock_get_ubuntu_codename:
            with self.patch_multiple_calls(self.side_effects) as mock_call:
                utils.add_apt_repository(self.repository)
        mock_get_ubuntu_codename.assert_called_once_with()
        self.assertEqual(len(self.side_effects), mock_call.call_count)
        mock_call.assert_has_calls([
            mock.call('sudo', self.apt_get, 'update'),
            mock.call('sudo', self.apt_get, 'install', '-y',
                      'python-software-properties'),
            mock.call('sudo', self.apt_add_repository, '-y', self.repository),
            mock.call('sudo', self.apt_get, 'update'),
        ])

    def test_after_precise(self, mock_print):
        # The repository is correctly added in newer releases.
        with self.patch_codename('trusty') as mock_get_ubuntu_codename:
            with self.patch_multiple_calls(self.side_effects) as mock_call:
                utils.add_apt_repository(self.repository)
        mock_get_ubuntu_codename.assert_called_once_with()
        self.assertEqual(len(self.side_effects), mock_call.call_count)
        mock_call.assert_has_calls([
            mock.call('sudo', self.apt_get, 'update'),
            mock.call('sudo', self.apt_get, 'install', '-y',
                      'software-properties-common'),
            mock.call('sudo', self.apt_add_repository, '-y', self.repository),
            mock.call('sudo', self.apt_get, 'update'),
        ])

    def test_output(self, mock_print):
        # The user is properly informed about the process.
        with self.patch_codename('raring'):
            with self.patch_multiple_calls(self.side_effects):
                utils.add_apt_repository(self.repository)
        self.assertEqual(2, mock_print.call_count)
        mock_print.assert_has_calls([
            mock.call('adding the {} PPA repository'.format(self.repository)),
            mock.call('sudo privileges will be required for PPA installation'),
        ])

    def test_command_error(self, mock_print):
        # An OSError is raised if a command error occurs.
        side_effects = [(0, 'update', ''), (1, '', 'apt-get install error')]
        with self.patch_codename('quantal') as mock_get_ubuntu_codename:
            with self.patch_multiple_calls(side_effects) as mock_call:
                with self.assertRaises(OSError) as context_manager:
                    utils.add_apt_repository(self.repository)
        mock_get_ubuntu_codename.assert_called_once_with()
        self.assertEqual(len(side_effects), mock_call.call_count)
        mock_call.assert_has_calls([
            mock.call('sudo', self.apt_get, 'update'),
            mock.call(
                'sudo', self.apt_get, 'install', '-y',
                'software-properties-common'),
        ])
        self.assertEqual(
            'apt-get install error', bytes(context_manager.exception))


class TestCall(unittest.TestCase):

    def test_success(self):
        # A zero exit code and the subprocess output are correctly returned.
        retcode, output, error = utils.call('echo')
        self.assertEqual(0, retcode)
        self.assertEqual('\n', output)
        self.assertEqual('', error)

    def test_multiple_arguments(self):
        # A zero exit code and the subprocess output are correctly returned
        # when executing a command passing multiple arguments.
        retcode, output, error = utils.call('echo', 'we are the borg!')
        self.assertEqual(0, retcode)
        self.assertEqual('we are the borg!\n', output)
        self.assertEqual('', error)

    def test_failure(self):
        # An error code and the error are returned if the subprocess fails.
        retcode, output, error = utils.call('ls', 'no-such-file')
        self.assertNotEqual(0, retcode)
        self.assertEqual('', output)
        self.assertIn('No such file or directory', error)

    def test_invalid_command(self):
        # An error code and the error are returned if the subprocess fails to
        # find the provided command in the PATH.
        retcode, output, error = utils.call('no-such-command')
        self.assertEqual(127, retcode)
        self.assertEqual('', output)
        self.assertEqual(
            'no-such-command: [Errno 2] No such file or directory',
            error)

    def test_logging(self):
        # The command line call and the results are properly logged.
        expected_messages = (
            "running the following: echo 'we are the borg!'",
            r"retcode: 0 | output: 'we are the borg!\n' | error: ''",
        )
        with helpers.assert_logs(expected_messages):
            utils.call('echo', 'we are the borg!')


class TestGetQuickstartBanner(unittest.TestCase):

    def patch_datetime(self):
        mock_datetime = mock.Mock()
        mock_datetime.utcnow.return_value = datetime.datetime(
            2014, 2, 27, 7, 42, 47)
        return mock.patch('datetime.datetime', mock_datetime)

    def test_banner(self):
        # The banner is correctly generated.
        with self.patch_datetime():
            obtained = utils.get_quickstart_banner()
        expected = (
            '# This file has been generated by juju quickstart v{}\n'
            '# at 2014-02-27 07:42:47 UTC.\n\n'
        ).format(get_version())
        self.assertEqual(expected, obtained)


class TestGetUbuntuCodename(helpers.CallTestsMixin, unittest.TestCase):

    def test_codename(self):
        # The distribution codename is correctly returned.
        with self.patch_call(0, output='trusty\n') as mock_call:
            codename = utils.get_ubuntu_codename()
        self.assertEqual('trusty', codename)
        mock_call.assert_called_once_with('lsb_release', '-cs')

    def test_error_retrieving_codename(self):
        # An OSError is returned if the codename cannot be retrieved.
        with self.patch_call(1, error='bad wolf') as mock_call:
            with self.assertRaises(OSError) as context_manager:
                utils.get_ubuntu_codename()
        self.assertEqual('bad wolf', bytes(context_manager.exception))
        mock_call.assert_called_once_with('lsb_release', '-cs')


class TestMkdir(unittest.TestCase):

    def setUp(self):
        # Set up a playground directory.
        self.playground = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.playground)

    def test_create_dir(self):
        # A directory is correctly created.
        path = os.path.join(self.playground, 'foo')
        utils.mkdir(path)
        self.assertTrue(os.path.isdir(path))

    def test_intermediate_dirs(self):
        # All intermediate directories are created.
        path = os.path.join(self.playground, 'foo', 'bar', 'leaf')
        utils.mkdir(path)
        self.assertTrue(os.path.isdir(path))

    def test_expand_user(self):
        # The ~ construction is expanded.
        with mock.patch('os.environ', {'HOME': self.playground}):
            utils.mkdir('~/in/my/home')
        path = os.path.join(self.playground, 'in', 'my', 'home')
        self.assertTrue(os.path.isdir(path))

    def test_existing_dir(self):
        # The function exits without errors if the target directory exists.
        path = os.path.join(self.playground, 'foo')
        os.mkdir(path)
        utils.mkdir(path)

    def test_existing_file(self):
        # An OSError is raised if a file already exists in the target path.
        path = os.path.join(self.playground, 'foo')
        with open(path, 'w'):
            with self.assertRaises(OSError):
                utils.mkdir(path)

    def test_failure(self):
        # Errors are correctly re-raised.
        path = os.path.join(self.playground, 'foo')
        os.chmod(self.playground, 0000)
        self.addCleanup(os.chmod, self.playground, 0700)
        with self.assertRaises(OSError):
            utils.mkdir(os.path.join(path))
        self.assertFalse(os.path.exists(path))


class TestRunOnce(unittest.TestCase):

    def setUp(self):
        self.results = []
        self.func = utils.run_once(self.results.append)

    def test_runs_once(self):
        # The wrapped function runs only the first time it is invoked.
        self.func(1)
        self.assertEqual([1], self.results)
        self.func(2)
        self.assertEqual([1], self.results)

    def test_wrapped(self):
        # The wrapped function looks like the original one.
        self.assertEqual('append', self.func.__name__)
        self.assertEqual(list.append.__doc__, self.func.__doc__)


class TestGetJujuVersion(
        helpers.CallTestsMixin, helpers.ValueErrorTestsMixin,
        unittest.TestCase):

    def test_return_deconstructed_version(self):
        # Should return a deconstructed juju version.
        with self.patch_call(0, '1.17.1-precise-amd64\n', ''):
            version = utils.get_juju_version('juju')
        self.assertEqual((1, 17, 1), version)

    def test_juju_version_error(self):
        # A ValueError is raised if "juju version" exits with an error.
        with self.patch_call(1, 'foo', 'bad wolf'):
            with self.assert_value_error('bad wolf'):
                utils.get_juju_version('juju')

    def test_alpha_version_string(self):
        # Patch level defaults to zero.
        with self.patch_call(0, '1.17-alpha1-precise-amd64', ''):
            version = utils.get_juju_version('juju')
        self.assertEqual((1, 17, 0), version)

    def test_invalid_version_string(self):
        # A ValueError is raised if "juju version" outputs an invalid version.
        with self.patch_call(0, '1-precise-amd64', ''):
            with self.assert_value_error('invalid version string: 1'):
                utils.get_juju_version('juju')
