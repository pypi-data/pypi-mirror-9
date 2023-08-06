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

"""Juju Quickstart API client."""

from __future__ import unicode_literals

import logging
import ssl

import jujuclient
import websocket


# Define the constant tag used by Juju for user entities.
JUJU_USER_TAG = 'user'
OPCODE_TEXT = websocket.ABNF.OPCODE_TEXT
# Define the options used to initiate the secure WebSocket connection.
SSLOPT = {
    'cert_reqs': ssl.CERT_NONE,
    'ssl_version': ssl.PROTOCOL_TLSv1,
}


def connect(api_url):
    """Return an Environment instance connected to the given API URL."""
    connection = WebSocketConnection(sslopt=SSLOPT)
    # See the websocket.create_connection function.
    connection.settimeout(websocket.default_timeout)
    connection.connect(api_url, origin=api_url)
    return Environment(api_url, conn=connection)


class Environment(jujuclient.Environment):
    """A Juju bootstrapped environment.

    Instances of this class can be used to run API operations on a Juju
    environment. Specifically this subclass enables bundle support and
    deployments to specific machines.
    """

    def authenticate(self, username, password):
        """Log in into the Juju environment with the given credentials.

        The user name must be provided without the default Juju prefix for
        users. Use self.login to log in specifying the complete user tag.
        """
        return self.login(
            password, user='{}-{}'.format(JUJU_USER_TAG, username))

    def deploy_bundle(self, yaml, version, bundle_id=None):
        """Deploy a bundle."""
        params = {'YAML': yaml}
        if version > 3:
            params['Version'] = version
        if bundle_id is not None:
            params['BundleID'] = bundle_id
        request = {
            'Type': 'Deployer',
            'Request': 'Import',
            'Params': params,
        }
        return self._rpc(request)

    def create_auth_token(self):
        """Make an auth token creation request.

        Here is an example of a successful token creation response.

            {
                'RequestId': 42,
                'Response': {
                    'Token': 'TOKEN-STRING',
                    'Created': '2013-11-21T12:34:46.778866Z',
                    'Expires': '2013-11-21T12:36:46.778866Z'
                }
            }
        """
        request = dict(Type='GUIToken', Request='Create')
        return self._rpc(request)

    def get_watcher(self):
        """Return a connected/authenticated environment watcher.

        This method is similar to jujuclient.Environment.get_watch, but it
        enables logging on the resulting watcher requests/responses traffic.
        """
        # Logging is enabled by the connect factory function, which uses our
        # customized WebSocketConnection. Note that, since jujuclient does not
        # track request identifiers, it is not currently possible to avoid
        # establishing a new connection for each watcher.
        env = connect(self.endpoint)
        # For the remaining bits, see jujuclient.Environment.get_watch.
        env.login(**self._creds)
        watcher = jujuclient.Watcher(env.conn)
        self._watches.append(watcher)
        watcher.start()
        return watcher

    def get_status(self):
        """Return the current status of the environment.

        The status is represented by a single mega-watcher changeset.
        Each change in the changeset is a tuple (entity, action, data) where:
            - entity is a string representing the changed content type
              (e.g. "service" or "unit");
            - action is a string representing the event which generated the
              change (i.e. "change" or "remove");
            - data is a dict containing information about the releated entity.
        """
        with self.get_watcher() as watcher:
            changeset = watcher.next()
        return changeset

    def watch_changes(self, processor):
        """Start watching the changes occurring in the Juju environment.

        For each changeset, call the given processor callable, and yield
        the values returned by the processor.
        """
        with self.get_watcher() as watcher:
            # The watcher closes when the context manager exit hook is called.
            for changeset in watcher:
                changes = processor(changeset)
                if changes:
                    yield changes


class WebSocketConnection(websocket.WebSocket):
    """A WebSocket client connection."""

    def send(self, payload, opcode=OPCODE_TEXT):
        """Send the given WebSocket message.

        Overridden to add logging in the case the payload is text.
        """
        if opcode == OPCODE_TEXT:
            message = payload.decode('utf-8', 'ignore')
            logging.debug('API message: --> {}'.format(message))
        return super(WebSocketConnection, self).send(payload, opcode=opcode)

    def recv(self):
        """Receive a message from the WebSocket server.

        Overridden to add logging in the case the received data is text.
        """
        data = super(WebSocketConnection, self).recv()
        if isinstance(data, bytes):
            message = data.decode('utf-8', 'ignore')
            logging.debug('API message: <-- {}'.format(message))
        return data
