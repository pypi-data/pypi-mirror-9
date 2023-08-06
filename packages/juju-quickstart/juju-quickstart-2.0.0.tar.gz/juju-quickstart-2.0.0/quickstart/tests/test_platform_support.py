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

"""Tests for the Juju Quickstart platform management."""

from __future__ import unicode_literals

import mock
import unittest

from quickstart import (
    platform_support,
    settings,
)
from quickstart.tests import helpers


def patch_isfile(files):
    def has_file(file):
        return file in files
    mock_patch_isfile = mock.Mock(side_effect=has_file)
    path = 'quickstart.platform_support.os.path.isfile'
    return mock.patch(path, mock_patch_isfile)


class TestGetPlatform(unittest.TestCase):

    def patch_platform_system(self, system=None):
        """Patch the platform.system call to return the given value."""
        mock_patch_platform = mock.Mock(return_value=system)
        path = 'quickstart.platform_support.platform.system'
        return mock.patch(path, mock_patch_platform)

    def test_linux_apt(self):
        with self.patch_platform_system('Linux'):
            with patch_isfile(['/usr/bin/apt-get']):
                result = platform_support.get_platform()
        self.assertEqual(settings.LINUX_APT, result)

    def test_linux_rpm(self):
        with self.patch_platform_system('Linux'):
            with patch_isfile(['/usr/bin/rpm']):
                result = platform_support.get_platform()
        self.assertEqual(settings.LINUX_RPM, result)

    def test_osx(self):
        with self.patch_platform_system('Darwin'):
            result = platform_support.get_platform()
        self.assertEqual(settings.OSX, result)

    def test_windows(self):
        with self.patch_platform_system('Windows'):
            result = platform_support.get_platform()
        self.assertEqual(settings.WINDOWS, result)

    def test_unsupported_raises_exception(self):
        with self.patch_platform_system('CP/M'):
            result = platform_support.get_platform()
        self.assertEqual(settings.UNKNOWN_PLATFORM, result)

    def test_linux_no_apt_nor_rpm_raises_exception(self):
        with self.patch_platform_system('Linux'):
            with patch_isfile([]):
                result = platform_support.get_platform()
        self.assertEqual(settings.LINUX_UNKNOWN, result)

    def test_null_system(self):
        # If platform.system cannot determine the OS it returns ''.  We have a
        # special case to return a meaningful message in that situation.
        with self.patch_platform_system(''):
            result = platform_support.get_platform()
        self.assertEqual(settings.UNKNOWN_PLATFORM, result)


class TestSupportLocal(unittest.TestCase):

    def test_support_local(self):
        expected = {
            settings.LINUX_APT: True,
            settings.LINUX_RPM: True,
            settings.OSX: False,
            settings.WINDOWS: False,
            object(): False,
        }
        for key, value in expected.items():
            self.assertEqual(value, platform_support.supports_local(key))


class TestGetJujuInstaller(helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_linux_apt(self):
        platform = settings.LINUX_APT
        installer = platform_support.get_juju_installer(platform)
        self.assertEqual(platform_support._installer_apt, installer)

    def test_osx(self):
        platform = settings.OSX
        installer = platform_support.get_juju_installer(platform)
        self.assertEqual(platform_support._installer_osx, installer)

    def test_linux_rpm(self):
        platform = settings.LINUX_RPM
        expected_error = 'No installer found for host platform.'
        with self.assert_value_error(expected_error):
            platform_support.get_juju_installer(platform)

    def test_windows(self):
        platform = settings.WINDOWS
        expected_error = 'No installer found for host platform.'
        with self.assert_value_error(expected_error):
            platform_support.get_juju_installer(platform)


class TestValidatePlatform(helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_osx_passes(self):
        with patch_isfile(['/usr/local/bin/brew']):
            result = platform_support.validate_platform(settings.OSX)
        self.assertIsNone(result)

    def test_osx_fails(self):
        with patch_isfile([]):
            expected_error = (
                'juju-quickstart requires brew to be installed on OS X. '
                'To install brew, see http://brew.sh'
            )
            with self.assert_value_error(expected_error):
                platform_support.validate_platform(settings.OSX)

    def test_linux_rpm_fails(self):
        expected_error = (
            'juju-quickstart on RPM-based Linux is not yet supported')
        with self.assert_value_error(expected_error):
            platform_support.validate_platform(settings.LINUX_RPM)

    def test_windows_fails(self):
        expected_error = 'juju-quickstart on Windows is not yet supported'
        with self.assert_value_error(expected_error):
            platform_support.validate_platform(settings.WINDOWS)

    def test_unknown_fails(self):
        expected_error = 'unable to determine the OS platform'
        with self.assert_value_error(expected_error):
            platform_support.validate_platform(settings.UNKNOWN_PLATFORM)

    def test_linux_unknown_fails(self):
        expected_error = 'unsupported Linux without apt-get nor rpm'
        with self.assert_value_error(expected_error):

            platform_support.validate_platform(settings.LINUX_UNKNOWN)

    def test_linux_apt_passes(self):
        result = platform_support.validate_platform(settings.LINUX_APT)
        self.assertIsNone(result)


class TestGetJujuCommand(unittest.TestCase):

    def test_getenv_succeeds(self):
        expected_command = '/custom/juju'
        with mock.patch('os.environ', {'JUJU': expected_command}):
            command, customized = platform_support.get_juju_command(None)
        self.assertEqual(expected_command, command)
        self.assertTrue(customized)

    def test_without_env_var(self):
        expected = settings.JUJU_CMD_PATHS['default'], False
        actual = platform_support.get_juju_command('default')
        self.assertEqual(expected, actual)
