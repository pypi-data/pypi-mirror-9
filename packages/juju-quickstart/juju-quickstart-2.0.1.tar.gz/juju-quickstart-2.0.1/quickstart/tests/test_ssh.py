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

"""Tests for the Juju Quickstart SSH management functions."""

from __future__ import unicode_literals

import os
import unittest

import mock

from quickstart import ssh
from quickstart.tests import helpers


class TestCheckKeys(helpers.CallTestsMixin, unittest.TestCase):

    def test_keys_and_agent(self):
        with self.patch_call(retcode=0) as mock_call:
            have_keys = ssh.check_keys()
        mock_call.assert_called_once_with('/usr/bin/ssh-add', '-l')
        self.assertTrue(have_keys)

    def test_agent_no_keys_success(self):
        side_effects = (
            (1, 'The agent has no identities.\n', ''),
            (0, '', ''),
        )
        with self.patch_multiple_calls(side_effects) as mock_call:
            have_keys = ssh.check_keys()
        mock_call.assert_has_calls([
            mock.call('/usr/bin/ssh-add', '-l'),
            mock.call('/usr/bin/ssh-add'),
        ])
        self.assertTrue(have_keys)

    def test_agent_no_keys_failure(self):
        side_effects = (
            (1, 'The agent has no identities.\n', ''),
            (1, 'Still no identities...', ''),
        )
        with self.patch_multiple_calls(side_effects) as mock_call:
            have_keys = ssh.check_keys()
        mock_call.assert_has_calls([
            mock.call('/usr/bin/ssh-add', '-l'),
            mock.call('/usr/bin/ssh-add'),
        ])
        self.assertFalse(have_keys)

    def test_agent_bad_keys(self):
        side_effects = (
            (1, 'The agent has no identities.\n', ''),
            (2, '', 'Oh no!'),
        )
        with self.assertRaises(OSError) as context_manager:
            with self.patch_multiple_calls(side_effects) as mock_call:
                ssh.check_keys()
        self.assertEqual(
            b'error attempting to add ssh keys: Oh no!',
            bytes(context_manager.exception))
        mock_call.assert_has_calls([
            mock.call('/usr/bin/ssh-add', '-l'),
            mock.call('/usr/bin/ssh-add'),
        ])

    def test_no_agent(self):
        with self.patch_call(retcode=2) as mock_call:
            have_keys = ssh.check_keys()
        mock_call.assert_called_once_with('/usr/bin/ssh-add', '-l')
        self.assertFalse(have_keys)


@helpers.mock_print
class TestCreateKeys(helpers.CallTestsMixin, unittest.TestCase):

    def test_success(self, mock_print):
        key_file = os.path.join(os.path.expanduser('~'), '.ssh', 'id_rsa')
        with self.patch_call(retcode=0) as mock_call:
            ssh.create_keys()
        mock_call.assert_has_calls([
            mock.call('/usr/bin/ssh-keygen',
                      '-q', '-b', '4096', '-t', 'rsa',
                      '-C',
                      'Generated with Juju Quickstart',
                      '-f', key_file),
            mock.call('/usr/bin/ssh-add')
        ])
        mock_print.assert_called_with(
            'a new ssh key was generated in {}'.format(key_file))

    def test_failure(self, mock_print):
        with self.assertRaises(OSError) as context_manager:
            with self.patch_call(retcode=1, error='Oh no!') as mock_call:
                ssh.create_keys()
        self.assertEqual(
            b'error generating ssh key: Oh no!',
            bytes(context_manager.exception))
        self.assertTrue(mock_call.called)
        side_effects = ((0, '', ''), (1, '', 'Oh no!'))
        with self.assertRaises(OSError) as context_manager:
            with self.patch_multiple_calls(side_effects) as mock_call:
                ssh.create_keys()
        self.assertEqual(
            b'error adding key to agent: Oh no!',
            bytes(context_manager.exception))
        self.assertTrue(mock_call.called)


@helpers.mock_print
class TestStartAgent(helpers.CallTestsMixin, unittest.TestCase):

    def test_success(self, mock_print):
        out = 'SSH_AUTH_SOCK=/tmp/ssh-authsock/agent.21000; ' \
              'export SSH_AUTH_SOCK;\n' \
              'SSH_AGENT_PID=21001; export SSH_AGENT_PID;\n' \
              'echo Agent pid 21001;'
        with self.patch_call(0, out, '') as mock_call:
            with mock.patch('os.putenv') as mock_putenv:
                ssh.start_agent()
        mock_call.assert_called_once_with('/usr/bin/ssh-agent')
        mock_putenv.assert_has_calls([
            mock.call('SSH_AUTH_SOCK', '/tmp/ssh-authsock/agent.21000'),
            mock.call('SSH_AGENT_PID', '21001'),
        ])
        mock_print.assert_called_once_with(
            'ssh-agent has been started.\nTo interact with Juju or quickstart '
            'again after quickstart\nfinishes, please run the following in a '
            'terminal to start ssh-agent:\n  eval `ssh-agent`\n')

    def test_failure(self, mock_print):
        with self.patch_call(1, 'Cannot start agent!', '') as mock_call:
            with self.assertRaises(OSError):
                ssh.start_agent()
        self.assertTrue(mock_call.called)


@mock.patch('time.sleep')
@helpers.mock_print
class TestWatchForKeys(helpers.CallTestsMixin, unittest.TestCase):

    print_message_call = mock.call(
        'Please run this command in another terminal or window and follow\n'
        'the instructions it produces; quickstart will continue when keys\n'
        'are generated, or ^C to quit.\n\n  ssh-keygen -b 4096 -t rsa\n\n'
        'Waiting...'
    )

    def test_watch(self, mock_print, mock_sleep):
        with mock.patch('quickstart.ssh.check_keys',
                        mock.Mock(side_effect=(False, True))):
            ssh.watch_for_keys()
        mock_print.assert_has_calls([
            self.print_message_call, mock.call('.', end='')])
        mock_sleep.assert_called_once_with(3)

    def test_cancel(self, mock_print, mock_sleep):
        with mock.patch('quickstart.ssh.check_keys',
                        mock.Mock(side_effect=KeyboardInterrupt)):
            with mock.patch('sys.exit') as mock_exit:
                ssh.watch_for_keys()
        mock_print.assert_has_calls([self.print_message_call])
        mock_exit.assert_called_once_with('\nquitting')
