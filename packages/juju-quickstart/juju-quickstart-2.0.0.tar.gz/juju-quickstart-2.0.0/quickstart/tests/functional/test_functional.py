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

"""Functional tests for Juju Quickstart."""

from __future__ import unicode_literals

import functools
import json
import os
import unittest

import quickstart
from quickstart import (
    platform_support,
    settings,
    utils,
)
from quickstart.models import envs


# Define the name of the environment variable used to run the functional tests.
FTEST_ENV_VAR = 'JUJU_QUICKSTART_FTESTS'


def skip_or_fail_if_environment_not_ready(func):
    """Decorate a test method so that it is only run when asked.

    Also fail if the Juju environment is already running, or if the default
    environment cannot be found.
    """
    # Check that functional tests are enabled.
    if os.getenv(FTEST_ENV_VAR) != '1':
        return unittest.skip(
            'to run functional tests, set {} to "1"'.format(FTEST_ENV_VAR))

    @functools.wraps(func)
    def decorated(cls_or_self):
        # If the environment cannot be found, or it is already running,
        # do not proceed with setting up the test case class, and make the
        # tests fail by setting env_error on the class or instance.
        cls_or_self.env_error = None
        # Check that a Juju environment can be found.
        env_name = envs.get_default_env_name()
        if env_name is None:
            cls_or_self.env_error = 'cannot find a configured Juju environment'
            return
        # Check that the Juju environment is not running.
        retcode, _, _ = run_juju('status', '-e', env_name)
        if not retcode:
            cls_or_self.env_error = (
                'the {} Juju environment is already running'.format(env_name))
            return
        # Update the received class or instance setting the env_name attribute.
        cls_or_self.env_name = env_name
        return func(cls_or_self)

    return decorated


def skip_if_environment_not_set(func):
    """Decorate a test method so that it is not run without an environment.

    The presence of the "env_name" attribute in the TestCase indicates whether
    or not the tests can be run.
    """
    @functools.wraps(func)
    def decorated(cls_or_self):
        if hasattr(cls_or_self, 'env_name'):
            return func(cls_or_self)

    return decorated


def run_juju(*args):
    """Run the juju command with the given args.

    Return a tuple including the command exit code, its output and error.
    """
    platform = platform_support.get_platform()
    cmd, _ = platform_support.get_juju_command(platform)
    return utils.call(cmd, *args)


def run_quickstart(env_name, *args):
    """Run the Juju Quickstart command.

    Return a tuple including the command exit code, its output and error.
    """
    package_dir = os.path.dirname(quickstart.__file__)
    cmd = os.path.abspath(os.path.join(package_dir, '..', 'juju-quickstart'))
    return utils.call(
        cmd, '-e', env_name, '--distro-only', '--no-browser', *args)


class TestFunctional(unittest.TestCase):

    @classmethod
    @skip_or_fail_if_environment_not_ready
    def setUpClass(cls):
        # Run Juju Quickstart to bootstrap Juju and deploy the Juju GUI.
        # Note that this is done once per suite. The resulting environment is
        # then destroyed when the suite completes.
        cls.retcode, cls.output, cls.error = run_quickstart(cls.env_name)

    @classmethod
    @skip_if_environment_not_set
    def tearDownClass(cls):
        # Destroy the environment.
        run_juju('destroy-environment', cls.env_name, '-y', '--force')

    def setUp(self):
        # Let all the tests fail if an environment error has been detected
        # in setUpClass.
        if self.env_error is not None:
            self.fail(self.env_error)

    def test_executed(self):
        # The application successfully completed its execution.
        self.assertEqual(0, self.retcode)
        self.assertIn('done!', self.output)
        self.assertEqual('', self.error)

    def test_gui_started(self):
        # At the end of the process, the Juju GUI unit is started.
        retcode, output, _ = run_juju(
            'status', '-e', self.env_name, '--format', 'json')
        self.assertEqual(0, retcode)
        status = json.loads(output)
        # The Juju GUI service is exposed.
        service = status['services'][settings.JUJU_GUI_SERVICE_NAME]
        self.assertTrue(service['exposed'])
        # The Juju GUI unit is started.
        unit = service['units']['{}/0'.format(settings.JUJU_GUI_SERVICE_NAME)]
        self.assertEqual('started', unit['agent-state'])

    def test_idempotent(self):
        # The application can be run again on an already bootstrapped
        # environment.
        retcode, output, error = run_quickstart(self.env_name)
        self.assertEqual(0, retcode)
        msg = 'reusing the already bootstrapped {} environment'
        self.assertIn(msg.format(self.env_name), output)
        self.assertEqual('', error)

    def test_version(self):
        # The application correctly prints out its own version.
        retcode, output, error = run_quickstart(self.env_name, '--version')
        self.assertEqual(0, retcode)
        self.assertEqual('', output)
        self.assertEqual(
            'juju-quickstart {}\n'.format(quickstart.get_version()), error)

    def test_bundle_deployment(self):
        # The application can be used to deploy bundles.
        retcode, output, error = run_quickstart(
            self.env_name, 'mediawiki-single')
        self.assertEqual(0, retcode)
        self.assertIn('bundle deployment request accepted', output)
        self.assertEqual('', error)
