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

"""Tests for the Juju Quickstart MAAS support."""

from __future__ import unicode_literals

import os
import shutil
import tempfile
import unittest

import mock

from quickstart import maas
from quickstart.tests import helpers


class TestCliAvailable(unittest.TestCase):

    def setUp(self):
        # Set up a a container for MAAS CLI tests.
        self.playground = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.playground)

    def test_not_found(self):
        # The MAAS CLI is not installed and cannot be found.
        path = os.path.join(self.playground, 'no-such')
        with mock.patch('quickstart.maas.settings.MAAS_CMD', path):
            self.assertFalse(maas.cli_available())

    def test_not_executable(self):
        # The file is not executable and for this reason the MAAS CLI is not
        # considered available.
        path = os.path.join(self.playground, 'not-executable')
        open(path, 'w').close()
        with mock.patch('quickstart.maas.settings.MAAS_CMD', path):
            self.assertFalse(maas.cli_available())

    def test_available(self):
        # The MAAS CLI is there and ready to be called.
        path = os.path.join(self.playground, 'executable')
        open(path, 'w').close()
        os.chmod(path, 0744)
        with mock.patch('quickstart.maas.settings.MAAS_CMD', path):
            self.assertTrue(maas.cli_available())


class TestGetApiInfo(helpers.CallTestsMixin, unittest.TestCase):

    def test_command_error(self):
        # None is returned and a warning is printed if the MAAS command returns
        # an error.
        expected_log = 'unable to list MAAS remote APIs: bad wolf'
        with self.patch_call(1, '', 'bad wolf'):
            with helpers.assert_logs([expected_log], level='warn'):
                api_info = maas.get_api_info()
        self.assertIsNone(api_info)

    def test_no_apis(self):
        # None is returned if no remote APIs are detected.
        with self.patch_call(0, '', ''):
            with helpers.assert_logs([], level='warn'):
                api_info = maas.get_api_info()
        self.assertIsNone(api_info)

    def test_malformed_output(self):
        # None is returned and a warning is printed if the MAAS command returns
        # an unexpected output.
        expected_log = 'unexpected response from MAAS CLI: exterminate!'
        with self.patch_call(0, 'exterminate!', ''):
            with helpers.assert_logs([expected_log], level='warn'):
                api_info = maas.get_api_info()
        self.assertIsNone(api_info)

    def test_info(self):
        # If at least one remote MAAS API is detected, then a tuple including
        # the MAAS name, address and API key is returned.
        output = 'maas-name http://1.2.3.4/MAAS/api/v1 maas:secret!'
        with self.patch_call(0, output, ''):
            with helpers.assert_logs([], level='warn'):
                api_info = maas.get_api_info()
        self.assertEqual(
            ('maas-name', 'http://1.2.3.4/MAAS', 'maas:secret!'),
            api_info)
