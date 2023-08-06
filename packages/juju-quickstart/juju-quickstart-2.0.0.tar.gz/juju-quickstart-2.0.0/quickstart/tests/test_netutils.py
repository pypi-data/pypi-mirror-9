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

"""Tests for the Juju Quickstart network utility functions."""

from __future__ import unicode_literals

import httplib
import json
import socket
import unittest
import urllib2

import mock

from quickstart import netutils
from quickstart.tests import helpers


class TestCheckResolvable(unittest.TestCase):

    def test_resolvable(self):
        # None is returned if the hostname can be resolved.
        expected_log = 'example.com resolved to 1.2.3.4'
        with helpers.assert_logs([expected_log], level='debug'):
            with mock.patch('socket.gethostbyname', return_value='1.2.3.4'):
                error = netutils.check_resolvable('example.com')
        self.assertIsNone(error)

    def test_not_resolvable(self):
        # An error message is returned if the hostname cannot be resolved.
        exception = socket.gaierror('bad wolf')
        with mock.patch('socket.gethostbyname', side_effect=exception):
            error = netutils.check_resolvable('example.com')
        self.assertEqual('bad wolf', error)


class TestCheckListening(unittest.TestCase):

    def test_listening(self):
        # None is returned if the address can be connected to.
        with helpers.patch_socket_create_connection() as mock_connection:
            error = netutils.check_listening('1.2.3.4:17070')
        self.assertIsNone(error)
        mock_connection.assert_called_once_with(('1.2.3.4', 17070), 3)

    def test_timeout(self):
        # A customized timeout can be passed.
        with helpers.patch_socket_create_connection() as mock_connection:
            error = netutils.check_listening('1.2.3.4:17070', timeout=42)
        self.assertIsNone(error)
        mock_connection.assert_called_once_with(('1.2.3.4', 17070), 42)

    def test_address_not_valid(self):
        # An error message is returned if the address is not valid.
        with helpers.patch_socket_create_connection() as mock_connection:
            error = netutils.check_listening('1.2.3.4')
        self.assertEqual(
            'cannot connect to 1.2.3.4: need more than 1 value to unpack',
            error)
        self.assertFalse(mock_connection.called)

    def test_port_not_valid(self):
        # An error message is returned if the address port is not valid.
        with helpers.patch_socket_create_connection() as mock_connection:
            error = netutils.check_listening('1.2.3.4:bad-port')
        self.assertEqual(
            'cannot connect to 1.2.3.4:bad-port: '
            "invalid literal for int() with base 10: 'bad-port'",
            error)
        self.assertFalse(mock_connection.called)

    def test_not_listening(self):
        # An error message is returned if the address is not reachable.
        with helpers.patch_socket_create_connection('boo!') as mock_connection:
            error = netutils.check_listening('1.2.3.4:17070')
        self.assertEqual('cannot connect to 1.2.3.4:17070: boo!', error)
        mock_connection.assert_called_once_with(('1.2.3.4', 17070), 3)

    def test_closing(self):
        # The socket connection is properly closed.
        with helpers.patch_socket_create_connection() as mock_connection:
            netutils.check_listening('1.2.3.4:17070')
        mock_connection().close.assert_called_once_with()

    def test_error_closing(self):
        # Errors closing the socket connection are ignored.
        with helpers.patch_socket_create_connection() as mock_connection:
            mock_connection().close.side_effect = socket.error('bad wolf')
            netutils.check_listening('1.2.3.4:17070')


class TestGetCharmUrl(helpers.UrlReadTestsMixin, unittest.TestCase):

    def test_charm_url(self):
        # The Juju GUI charm URL is correctly returned.
        contents = json.dumps({
            'Id': 'cs:trusty/juju-gui-42',
            'Series': 'trusty',
            'Name': 'juju-gui',
            'Revision': 42,
        })
        with self.patch_urlread(contents=contents) as mock_urlread:
            charm_url = netutils.get_charm_url('trusty')
        self.assertEqual('cs:trusty/juju-gui-42', charm_url)
        mock_urlread.assert_called_once_with(
            'https://api.jujucharms.com/charmstore/v4/trusty/juju-gui/meta/id')

    def test_io_error(self):
        # IOErrors are properly propagated.
        with self.patch_urlread(error=True) as mock_urlread:
            with self.assertRaises(IOError) as context_manager:
                netutils.get_charm_url('precise')
        mock_urlread.assert_called_once_with(
            'https://api.jujucharms.com/charmstore/v4/precise/juju-gui/meta/id'
        )
        self.assertEqual('bad wolf', bytes(context_manager.exception))

    def test_value_error(self):
        # A ValueError is raised if the API response is not valid.
        contents = json.dumps({'invalid': {}})
        with self.patch_urlread(contents=contents) as mock_urlread:
            with self.assertRaises(ValueError) as context_manager:
                netutils.get_charm_url('trusty')
        mock_urlread.assert_called_once_with(
            'https://api.jujucharms.com/charmstore/v4/trusty/juju-gui/meta/id')
        self.assertEqual(
            'unable to find the charm URL', bytes(context_manager.exception))


class TestUrlread(unittest.TestCase):

    def patch_urlopen(self, contents=None, error=None, content_type=None):
        """Patch the urllib2.urlopen function.

        If contents is not None, the read() method of the returned mock object
        returns the given contents.
        If content_type is provided, the response includes the content type.
        If an error is provided, the call raises the error.
        """
        mock_urlopen = mock.MagicMock()
        if contents is not None:
            mock_urlopen().read.return_value = contents
        if content_type is not None:
            mock_urlopen().headers = {'content-type': content_type}
        if error is not None:
            mock_urlopen.side_effect = error
        mock_urlopen.reset_mock()
        return mock.patch('urllib2.urlopen', mock_urlopen)

    def test_contents(self):
        # The URL contents are correctly returned.
        with self.patch_urlopen(contents=b'URL contents') as mock_urlopen:
            contents = netutils.urlread('http://example.com/path/')
        self.assertEqual('URL contents', contents)
        self.assertIsInstance(contents, unicode)
        mock_urlopen.assert_called_once_with('http://example.com/path/')

    def test_content_type(self):
        # The URL contents are decoded using the site charset.
        patch_urlopen = self.patch_urlopen(
            contents=b'URL contents: \xf8',  # This is not a UTF-8 byte string.
            content_type='text/html; charset=ISO-8859-1')
        with patch_urlopen as mock_urlopen:
            contents = netutils.urlread('http://example.com/path/')
        self.assertEqual('URL contents: \xf8', contents)
        self.assertIsInstance(contents, unicode)
        mock_urlopen.assert_called_once_with('http://example.com/path/')

    def test_no_content_type(self):
        # The URL contents are decoded with UTF-8 by default.
        patch_urlopen = self.patch_urlopen(
            contents=b'URL contents: \xf8',  # This is not a UTF-8 byte string.
            content_type='text/html')
        with patch_urlopen as mock_urlopen:
            contents = netutils.urlread('http://example.com/path/')
        self.assertEqual('URL contents: ', contents)
        self.assertIsInstance(contents, unicode)
        mock_urlopen.assert_called_once_with('http://example.com/path/')

    def test_errors(self):
        # An IOError is raised if an error occurs connecting to the API.
        errors = {
            'httplib HTTPException': httplib.HTTPException,
            'socket error': socket.error,
            'urllib2 URLError': urllib2.URLError,
        }
        for message, exception_class in errors.items():
            exception = exception_class(message)
            with self.patch_urlopen(error=exception) as mock_urlopen:
                with self.assertRaises(IOError) as context_manager:
                    netutils.urlread('http://example.com/path/')
            mock_urlopen.assert_called_once_with('http://example.com/path/')
            self.assertEqual(message, bytes(context_manager.exception))
