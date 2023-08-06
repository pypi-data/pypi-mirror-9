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

"""Tests for the Juju Quickstart serialization helpers."""

from __future__ import unicode_literals

import os
import tempfile
import unittest

import mock
import yaml

from quickstart import serializers
from quickstart.tests import helpers


class TestYamlLoad(unittest.TestCase):

    contents = '{myint: 42, mystring: foo}'

    def test_unicode_strings(self):
        # Strings are returned as unicode objects.
        decoded = serializers.yaml_load(self.contents)
        self.assertEqual(42, decoded['myint'])
        self.assertEqual('foo', decoded['mystring'])
        self.assertIsInstance(decoded['mystring'], unicode)
        for key in decoded:
            self.assertIsInstance(key, unicode, key)

    @mock.patch('quickstart.serializers.yaml.load')
    def test_safe(self, mock_load):
        # The YAML decoder uses a safe loader.
        serializers.yaml_load(self.contents)
        self.assertEqual(self.contents, mock_load.call_args[0][0])
        loader_class = mock_load.call_args[1]['Loader']
        self.assertTrue(issubclass(loader_class, yaml.SafeLoader))


class TestYamlDump(unittest.TestCase):

    data = {'myint': 42, 'mystring': 'foo'}

    def test_block_style(self):
        # Collections are serialized in the block style.
        contents = serializers.yaml_dump(self.data)
        self.assertEqual('myint: 42\nmystring: foo\n', contents)


class TestYamlLoadFromPath(helpers.ValueErrorTestsMixin, unittest.TestCase):

    def make_file(self, contents):
        """Create a temporary file with the given contents.

        Return the file path.
        """
        yaml_file = tempfile.NamedTemporaryFile(delete=False)
        self.addCleanup(os.remove, yaml_file.name)
        yaml_file.write(contents)
        yaml_file.close()
        return yaml_file.name

    def test_resulting_contents(self):
        # The YAML deserialized contents are correctly returned.
        expected_data = {'myint': 42, 'mystring': 'foo'}
        path = self.make_file(yaml.safe_dump(expected_data))
        obtained_data = serializers.yaml_load_from_path(path)
        self.assertEqual(expected_data, obtained_data)

    def test_no_file(self):
        # A ValueError is raised if the given file is not found.
        expected_error = (
            "unable to open file /no/such/file.yaml: "
            "[Errno 2] No such file or directory: '/no/such/file.yaml'"
        )
        with self.assert_value_error(expected_error):
            serializers.yaml_load_from_path('/no/such/file.yaml')

    def test_invalid_yaml(self):
        # A ValueError is raised if the given file is not a valid YAML.
        path = self.make_file(':')
        with self.assertRaises(ValueError) as context_manager:
            serializers.yaml_load_from_path(path)
        expected = 'unable to parse file {}'.format(path)
        self.assertIn(expected, bytes(context_manager.exception))
