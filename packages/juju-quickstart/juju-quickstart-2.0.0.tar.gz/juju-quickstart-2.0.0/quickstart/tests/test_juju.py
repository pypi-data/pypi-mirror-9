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

"""Tests for the Juju Quickstart API client."""

from __future__ import unicode_literals

import unittest

import mock
import websocket

from quickstart import juju
from quickstart.tests import helpers


patch_rpc = mock.patch('quickstart.juju.Environment._rpc')


class TestConnect(unittest.TestCase):

    api_url = 'wss://api.example.com:17070'

    @mock.patch('quickstart.juju.WebSocketConnection')
    def test_environment_connection(self, mock_conn):
        # A connected Environment instance is correctly returned.
        env = juju.connect(self.api_url)
        mock_conn.assert_called_once_with(sslopt=juju.SSLOPT)
        conn = mock_conn()
        conn.assert_has_calls([
            mock.call.settimeout(websocket.default_timeout),
            mock.call.connect(self.api_url, origin=self.api_url)
        ])
        self.assertIsInstance(env, juju.Environment)
        self.assertEqual(self.api_url, env.endpoint)
        self.assertEqual(conn, env.conn)


class TestEnvironment(unittest.TestCase):
    # Note that in some of the tests below, rather than exercising quickstart
    # code, we are actually testing the external jujuclient methods. This is so
    # by design, and will help us when upgrading the python-jujuclient library.

    api_url = 'wss://api.example.com:17070'
    charm_url = 'cs:precise/juju-gui-77'
    service_name = 'juju-gui'

    def setUp(self):
        # Set up an Environment instance.
        api_url = self.api_url
        with mock.patch('websocket.create_connection') as mock_connect:
            self.env = juju.Environment(api_url)
        # In old versions of jujuclient the SSL options are not passed as
        # kwargs to create_connection.
        if len(mock_connect.call_args[1]) == 1:
            mock_connect.assert_called_once_with(api_url, origin=api_url)
        else:
            mock_connect.assert_called_once_with(
                api_url, origin=api_url, sslopt=juju.SSLOPT)
        # Keep track of watcher changes in the changesets list.
        self.changesets = []

    def make_add_unit_request(self, **kwargs):
        """Create and return an "add unit" request.

        Use kwargs to add or override request parameters.
        """
        params = {
            'ServiceName': self.service_name,
            'NumUnits': 1,
        }
        params.update(kwargs)
        return {
            'Type': 'Client',
            'Request': 'AddServiceUnits',
            'Params': params,
        }

    def make_deploy_request(self, **kwargs):
        """Create and return a "deploy" request.

        Use kwargs to add or override request parameters.
        """
        params = {
            'ServiceName': self.service_name,
            'CharmURL': self.charm_url,
            'NumUnits': 1,
            'Config': {},
            'Constraints': {},
            'ToMachineSpec': None,
        }
        params.update(kwargs)
        return {
            'Type': 'Client',
            'Request': 'ServiceDeploy',
            'Params': params,
        }

    def patch_get_watcher(self, return_value):
        """Patch the Environment.get_watcher method.

        When the resulting mock is used as a context manager, the given return
        value is returned.
        """
        get_watcher_path = 'quickstart.juju.Environment.get_watcher'
        mock_get_watcher = mock.MagicMock()
        mock_get_watcher().__enter__.return_value = iter(return_value)
        mock_get_watcher.reset_mock()
        return mock.patch(get_watcher_path, mock_get_watcher)

    def processor(self, changeset):
        self.changesets.append(changeset)
        return changeset

    @patch_rpc
    def test_add_unit(self, mock_rpc):
        # The AddServiceUnits API call is properly generated.
        self.env.add_unit(self.service_name)
        mock_rpc.assert_called_once_with(self.make_add_unit_request())

    @patch_rpc
    def test_add_unit_to_machine(self, mock_rpc):
        # The AddServiceUnits API call is properly generated when deploying a
        # unit in a specific machine.
        self.env.add_unit(self.service_name, machine_spec='0')
        expected = self.make_add_unit_request(ToMachineSpec='0')
        mock_rpc.assert_called_once_with(expected)

    @patch_rpc
    def test_deploy(self, mock_rpc):
        # The deploy API call is properly generated.
        self.env.deploy(self.service_name, self.charm_url)
        mock_rpc.assert_called_once_with(self.make_deploy_request())

    @patch_rpc
    def test_deploy_config(self, mock_rpc):
        # The deploy API call is properly generated when passing settings.
        self.env.deploy(
            self.service_name, self.charm_url,
            config={'key1': 'value1', 'key2': 42})
        expected = self.make_deploy_request(
            Config={'key1': 'value1', 'key2': '42'})
        mock_rpc.assert_called_once_with(expected)

    @patch_rpc
    def test_deploy_constraints(self, mock_rpc):
        # The deploy API call is properly generated when passing constraints.
        constraints = {'cpu-cores': 8, 'mem': 16}
        self.env.deploy(
            self.service_name, self.charm_url, constraints=constraints)
        expected = self.make_deploy_request(Constraints=constraints)
        mock_rpc.assert_called_once_with(expected)

    @patch_rpc
    def test_deploy_no_units(self, mock_rpc):
        # The deploy API call is properly generated when passing zero units.
        self.env.deploy(self.service_name, self.charm_url, num_units=0)
        expected = self.make_deploy_request(NumUnits=0)
        mock_rpc.assert_called_once_with(expected)

    @patch_rpc
    def test_deploy_bundle_v3(self, mock_rpc):
        # The deploy bundle call is properly generated (API v3).
        self.env.deploy_bundle('name: contents', 3)
        expected = {
            'Type': 'Deployer',
            'Request': 'Import',
            'Params': {'YAML': 'name: contents'},
        }
        mock_rpc.assert_called_once_with(expected)

    @patch_rpc
    def test_deploy_bundle_v4(self, mock_rpc):
        # The deploy bundle call is properly generated (API v4).
        self.env.deploy_bundle('name: contents', 4)
        expected = {
            'Type': 'Deployer',
            'Request': 'Import',
            'Params': {'YAML': 'name: contents', 'Version': 4},
        }
        mock_rpc.assert_called_once_with(expected)

    @patch_rpc
    def test_deploy_bundle_with_bundle_id(self, mock_rpc):
        # The deploy bundle call is properly generated when passing a
        # bundle_id.
        self.env.deploy_bundle(
            'name: contents', 4, bundle_id='~celso/basquet/wiki')
        expected = {
            'Type': 'Deployer',
            'Request': 'Import',
            'Params': {
                'YAML': 'name: contents',
                'Version': 4,
                'BundleID': '~celso/basquet/wiki',
            },
        }
        mock_rpc.assert_called_once_with(expected)

    @patch_rpc
    def test_expose(self, mock_rpc):
        # The expose API call is properly generated.
        self.env.expose(self.service_name)
        expected = {
            'Type': 'Client',
            'Request': 'ServiceExpose',
            'Params': {'ServiceName': self.service_name},
        }
        mock_rpc.assert_called_once_with(expected)

    @patch_rpc
    def test_get_watcher(self, mock_rpc):
        # Environment watching is correctly started.
        self.env.login('Secret!')
        # We are only interested in the calls from now on.
        mock_rpc.reset_mock()
        connect_path = 'quickstart.juju.WebSocketConnection.connect'
        watcher_rpc_path = 'quickstart.juju.jujuclient.Watcher._rpc'
        with mock.patch(connect_path) as mock_connect:
            with mock.patch(watcher_rpc_path) as mock_watcher_rpc:
                watcher = self.env.get_watcher()
        # The returned watcher is running.
        self.assertTrue(watcher.running)
        # The watcher uses our customized WebSocket connection with logging.
        self.assertIsInstance(watcher.conn, juju.WebSocketConnection)
        # A connection has been established with the API backend.
        mock_connect.assert_called_once_with(self.api_url, origin=self.api_url)
        # The connection used by the watcher is authenticated.
        expected = {
            'Type': 'Admin',
            'Request': 'Login',
            'Params': {'AuthTag': 'user-admin', 'Password': 'Secret!'},
        }
        mock_rpc.assert_called_once_with(expected)
        # The watcher sent the correct start request.
        mock_watcher_rpc.assert_called_with({
            'Type': 'Client',
            'Request': 'WatchAll',
            'Params': {},
        })

    def test_get_status(self):
        # The current status of the Juju environment is properly returned.
        changesets = [['change1', 'change2'], ['change3']]
        with self.patch_get_watcher(changesets) as mock_get_watcher:
            status = self.env.get_status()
        # The get_status call only waits for the first changeset.
        self.assertEqual(changesets[0], status)
        # The watcher is correctly closed.
        self.assertEqual(1, mock_get_watcher().__exit__.call_count)

    @patch_rpc
    def test_login(self, mock_rpc):
        # The login API call is properly generated.
        self.env.login('Secret!')
        expected = {
            'Type': 'Admin',
            'Request': 'Login',
            'Params': {'AuthTag': 'user-admin', 'Password': 'Secret!'},
        }
        mock_rpc.assert_called_once_with(expected)

    @patch_rpc
    def test_authenticate(self, mock_rpc):
        # The authentication is performed with the given credentials.
        self.env.authenticate('who', 'passwd')
        expected = {
            'Type': 'Admin',
            'Request': 'Login',
            'Params': {'AuthTag': 'user-who', 'Password': 'passwd'},
        }
        mock_rpc.assert_called_once_with(expected)

    @patch_rpc
    def test_info(self, mock_rpc):
        # The EnvironmentInfo API call is properly generated.
        self.env.info()
        mock_rpc.assert_called_once_with({
            'Type': 'Client',
            'Request': 'EnvironmentInfo',
        })

    @patch_rpc
    def test_create_auth_token(self, mock_rpc):
        self.env.create_auth_token()
        expected = dict(Type='GUIToken', Request='Create')
        mock_rpc.assert_called_once_with(expected)

    def test_watch_changes(self):
        # It is possible to watch for changes using a processor callable.
        changesets = [['change1', 'change2'], ['change3']]
        with self.patch_get_watcher(changesets) as mock_get_watcher:
            watcher = self.env.watch_changes(self.processor)
            # The first set of changes is correctly returned.
            changeset = watcher.next()
            self.assertEqual(changesets[0], changeset)
            # The second set of changes is correctly returned.
            changeset = watcher.next()
            self.assertEqual(changesets[1], changeset)
        # All the changes have been processed.
        self.assertEqual(changesets, self.changesets)
        # Ensure the API has been used properly.
        mock_get_watcher().__enter__.assert_called_once_with()

    def test_watch_changes_map(self):
        # The processor callable can be used to modify changes.
        changeset1 = ['change1', 'change2']
        changeset2 = ['change3']
        with self.patch_get_watcher([changeset1, changeset2]):
            watcher = self.env.watch_changes(len)
            changesets = list(watcher)
        self.assertEqual([len(changeset1), len(changeset2)], changesets)

    def test_watch_changes_filter(self):
        # The processor callable can be used to filter changes.
        changeset1 = ['change1', 'change2']
        changeset2 = ['change3']
        processor = lambda changes: None if len(changes) == 1 else changes
        with self.patch_get_watcher([changeset1, changeset2]):
            watcher = self.env.watch_changes(processor)
            changesets = list(watcher)
        self.assertEqual([changeset1], changesets)

    def test_watch_closed(self):
        # A stop API call on the AllWatcher is performed when the watcher is
        # garbage collected.
        changeset = ['change1', 'change2']
        with self.patch_get_watcher([changeset]) as mock_get_watcher:
            watcher = self.env.watch_changes(self.processor)
            # The first set of changes is correctly returned.
            watcher.next()
            del watcher
        # Ensure the API has been used properly.
        self.assertEqual(1, mock_get_watcher().__exit__.call_count)


class TestWebSocketConnection(unittest.TestCase):

    snowman = 'Here is a snowman\u00a1: \u2603'

    def setUp(self):
        self.conn = juju.WebSocketConnection()

    def test_send(self):
        # Outgoing messages are properly logged.
        with helpers.assert_logs(['API message: --> my message'], 'debug'):
            with mock.patch('websocket.WebSocket.send') as mock_send:
                self.conn.send('my message')
        mock_send.assert_called_once_with(
            'my message', opcode=juju.OPCODE_TEXT)

    def test_send_unicode(self):
        # Outgoing unicode messages are properly logged.
        expected = 'API message: --> {}'.format(self.snowman)
        with helpers.assert_logs([expected], 'debug'):
            with mock.patch('websocket.WebSocket.send') as mock_send:
                self.conn.send(self.snowman.encode('utf-8'))
        mock_send.assert_called_once_with(
            self.snowman.encode('utf-8'), opcode=juju.OPCODE_TEXT)

    def test_send_not_text(self):
        # Outgoing non-textual messages are not logged.
        with helpers.assert_logs([], 'debug'):
            with mock.patch('websocket.WebSocket.send') as mock_send:
                self.conn.send(0x0, opcode=websocket.ABNF.OPCODE_BINARY)
        mock_send.assert_called_once_with(
            0x0, opcode=websocket.ABNF.OPCODE_BINARY)

    def test_recv(self):
        # Incoming messages are properly logged.
        with helpers.assert_logs(['API message: <-- my message'], 'debug'):
            with mock.patch('websocket.WebSocket.recv') as mock_recv:
                mock_recv.return_value = (b'my message')
                message = self.conn.recv()
        self.assertEqual('my message', message)

    def test_recv_unicode(self):
        # Incoming unicode messages are properly logged.
        expected = 'API message: <-- {}'.format(self.snowman)
        with helpers.assert_logs([expected], 'debug'):
            with mock.patch('websocket.WebSocket.recv') as mock_recv:
                mock_recv.return_value = self.snowman.encode('utf-8')
                message = self.conn.recv()
        self.assertEqual(self.snowman.encode('utf-8'), message)

    def test_recv_not_text(self):
        # Incoming non-textual messages are not logged.
        with helpers.assert_logs([], 'debug'):
            with mock.patch('websocket.WebSocket.recv') as mock_recv:
                mock_recv.return_value = 0x0
                self.conn.recv()
