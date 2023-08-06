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

"""Tests for the Juju Quickstart field definitions."""

from __future__ import unicode_literals

from contextlib import contextmanager
import os
import unittest

import mock

from quickstart.models import fields
from quickstart.tests import helpers


class FieldTestsMixin(object):
    """Define a collection of tests shared by all fields.

    Subclasses must define a field_class attribute.
    """

    @contextmanager
    def assert_not_raises(self, exception, message=None):
        """Ensure the given exception is not raised in the code block."""
        try:
            yield
        except exception as err:
            msg = b'unexpected {}: {}'.format(err.__class__.__name__, err)
            if message:
                msg += b' ({!r})'.format(message)
            self.fail(msg)

    def test_attributes(self):
        # The field attributes are properly stored in the field instance.
        field = self.field_class(
            'first-name', label='first name', help='your first name',
            default='default', required=True, readonly=False)
        self.assertEqual('first-name', field.name)
        self.assertEqual('first name', field.label)
        self.assertEqual('your first name', field.help)
        self.assertEqual('default', field.default)
        self.assertTrue(field.required)
        self.assertFalse(field.readonly)

    def test_default_attributes(self):
        # Only the name identifier is required when instantiating a field.
        field = self.field_class('last-name')
        self.assertEqual('last-name', field.name)
        self.assertEqual('last-name', field.label)
        self.assertEqual('', field.help)
        self.assertIsNone(field.default)
        self.assertFalse(field.required)
        self.assertFalse(field.readonly)

    def test_field_representation(self):
        # A field object is properly represented.
        field = self.field_class('email')
        expected = b'<{}: email>'.format(self.field_class.__name__)
        self.assertEqual(expected, repr(field))

    def test_display(self):
        # A field is able to display values.
        field = self.field_class('phone-number')
        for value in (None, 42, True, 'a unicode string'):
            self.assertEqual(unicode(value), field.display(value), value)


class TestField(
        FieldTestsMixin, helpers.ValueErrorTestsMixin, unittest.TestCase):

    field_class = fields.Field

    def test_normalization(self):
        # The base field normalization is a no-op if the value is set.
        field = self.field_class('email')
        for value in (None, 42, True, 'a unicode string'):
            self.assertEqual(value, field.normalize(value), value)

    def test_validation_success(self):
        # The validation succeeds if the value is set.
        field = self.field_class('email')
        for value in (42, True, 'a unicode string', ' '):
            self.assertIsNone(field.validate(value), value)

    def test_validation_not_required(self):
        # If the field is not required, no errors are raised.
        field = self.field_class('email', required=False)
        for value in ('', False, None):
            with self.assert_not_raises(ValueError, value):
                field.validate(value)

    def test_validation_error_required(self):
        # A ValueError is raised by required fields if the value is not set.
        field = self.field_class('email', label='email address', required=True)
        expected = 'a value is required for the email address field'
        with self.assert_value_error(expected):
            field.validate(None)

    def test_validation_with_default(self):
        # The validation succeeds if the value is unset but a default one is
        # available.
        field = self.field_class('answer', default=42, required=True)
        with self.assert_not_raises(ValueError):
            field.validate(None)


class TestStringField(
        FieldTestsMixin, helpers.ValueErrorTestsMixin, unittest.TestCase):

    field_class = fields.StringField

    def test_normalization(self):
        # The string field normalization returns the stripped string value.
        field = self.field_class('email')
        for value in ('a value', '\t tabs and spaces ', 'newlines\n\n'):
            self.assertEqual(value.strip(), field.normalize(value), value)

    def test_none_normalization(self):
        # The string field normalization returns None if the value is not set.
        field = self.field_class('email')
        for value in ('', '  ', '\n', ' \t ', None):
            self.assertIsNone(field.normalize(value), value)

    def test_validation_success(self):
        # The validation succeeds if the value is set.
        field = self.field_class('email')
        for value in ('a value', '\t tabs and spaces ', 'newlines\n\n'):
            self.assertIsNone(field.validate(value), value)

    def test_validation_not_required(self):
        # If the field is not required, no errors are raised.
        field = self.field_class('email', required=False)
        for value in ('', None, ' ', '\t\n'):
            with self.assert_not_raises(ValueError, value):
                field.validate(value)

    def test_validation_error_required(self):
        # A ValueError is raised by required fields if the value is not set.
        field = self.field_class('email', label='email address', required=True)
        expected = 'a value is required for the email address field'
        for value in ('', None, ' ', '\t\n'):
            with self.assert_value_error(expected):
                field.validate(value)

    def test_validation_error_not_a_string(self):
        # A ValueError is raised by string fields if the value is not a string.
        field = self.field_class('email', label='email address')
        expected = 'the email address field requires a string value'
        for value in (42, False, []):
            with self.assert_value_error(expected):
                field.validate(value)

    def test_validation_with_default(self):
        # The validation succeeds if the value is unset but a default one is
        # available.
        field = self.field_class(
            'email', default='email@example.com', required=True)
        with self.assert_not_raises(ValueError):
            field.validate(None)


class TestIntField(
        FieldTestsMixin, helpers.ValueErrorTestsMixin, unittest.TestCase):

    field_class = fields.IntField

    def test_normalization(self):
        # The int field normalization returns the values as integers.
        field = self.field_class('tcp-port')
        for value in (42, 42.0, '42', '\t42  ', '42\n\n'):
            self.assertEqual(42, field.normalize(value), value)

    def test_none_normalization(self):
        # The int field normalization returns None if the value is not set.
        field = self.field_class('tcp-port')
        for value in (None, '', ' ', '\t\n'):
            self.assertIsNone(field.normalize(value), value)

    def test_zero_normalization(self):
        # The zero value is not considered unset.
        field = self.field_class('tcp-port')
        self.assertEqual(0, field.normalize(0))

    def test_validation_success(self):
        # The value as an integer number is returned if the value is valid.
        field = self.field_class('tcp-port')
        for value in (42, 42.0, '42', '\t42  ', '42\n\n'):
            with self.assert_not_raises(ValueError, value):
                field.validate(value)

    def test_validation_success_zero(self):
        # The zero value is not considered "unset".
        field = self.field_class('tcp-port')
        with self.assert_not_raises(ValueError):
            field.validate(0)

    def test_validation_success_in_range(self):
        # The value as an integer number is returned if the value is valid and
        # is in the specified range of min/max values.
        field = self.field_class('tcp-port', min_value=42, max_value=47)
        for value in (42, 42.0, '42', '\t42  ', '42\n\n'):
            with self.assert_not_raises(ValueError, value):
                field.validate(value)

    def test_validation_not_required(self):
        # If the field is not required, no errors are raised.
        field = self.field_class('tcp-port', required=False)
        for value in ('', None, ' ', '\t\n'):
            with self.assert_not_raises(ValueError, value):
                self.assertIsNone(field.validate(value), value)

    def test_validation_error_required(self):
        # A ValueError is raised by required fields if the value is not set.
        field = self.field_class('tcp-port', label='TCP port', required=True)
        expected = 'a value is required for the TCP port field'
        for value in ('', None, ' ', '\t\n'):
            with self.assert_value_error(expected):
                field.validate(value)

    def test_validation_error_not_a_number(self):
        # A ValueError is raised by int fields if the value is not a number.
        field = self.field_class('tcp-port', label='TCP port')
        expected = 'the TCP port field requires an integer value'
        for value in ('a string', False, {}, []):
            with self.assert_value_error(expected):
                field.validate(value)

    def test_validation_error_min_value(self):
        # A ValueError is raised if value < min_value.
        field = self.field_class('tcp-port', min_value=42, label='TCP port')
        with self.assert_value_error('the TCP port value must be >= 42'):
            field.validate(27)

    def test_validation_error_max_value(self):
        # A ValueError is raised if value > max_value.
        field = self.field_class('tcp-port', max_value=42, label='TCP port')
        with self.assert_value_error('the TCP port value must be <= 42'):
            field.validate(47)

    def test_validation_error_range(self):
        # A ValueError is raised if not min_value <= value <= max_value.
        field = self.field_class(
            'tcp-port', min_value=42, max_value=47, label='TCP port')
        expected = 'the TCP port value must be in the 42-47 range'
        with self.assert_value_error(expected):
            field.validate(27)

    def test_validation_with_default(self):
        # The validation succeeds if the value is unset but a default one is
        # available.
        field = self.field_class('tcp-port', default=8888, required=True)
        with self.assert_not_raises(ValueError):
            field.validate(None)


class TestBoolField(
        FieldTestsMixin, helpers.ValueErrorTestsMixin, unittest.TestCase):

    field_class = fields.BoolField

    def test_default_attributes(self):
        # Only the name identifier is required when instantiating a field.
        field = self.field_class('is-public')
        self.assertEqual('is-public', field.name)
        self.assertEqual('is-public', field.label)
        self.assertEqual('', field.help)
        self.assertFalse(field.default)
        self.assertFalse(field.required)
        self.assertFalse(field.readonly)

    def test_normalization(self):
        # The bool field normalization returns the value itself.
        field = self.field_class('is-public')
        self.assertTrue(field.normalize(True))
        self.assertFalse(field.normalize(False))

    def test_none_normalization(self):
        # The string field normalization returns None if the value is not set.
        field = self.field_class('is-public')
        self.assertIsNone(field.normalize(None))

    def test_validation_success(self):
        # The validation succeeds if the value is boolean.
        field = self.field_class('is-public')
        with self.assert_not_raises(ValueError):
            field.validate(True)
            field.validate(False)

    def test_validation_error_not_a_boolean(self):
        # A ValueError is raised by string fields if the value is not a bool.
        field = self.field_class('is-public', label='is public')
        expected = 'the is public field requires a boolean value'
        for value in (42, 'a string', []):
            with self.assert_value_error(expected):
                field.validate(value)

    def test_validation_not_required(self):
        # If the field is not required, no errors are raised.
        field = self.field_class('is-public', required=False)
        with self.assert_not_raises(ValueError):
            field.validate(None)

    def test_validation_error_required(self):
        # If the value is not set, the default value will be used.
        field = self.field_class(
            'is-public', label='is public', default=False, required=True)
        with self.assert_not_raises(ValueError):
            field.validate(None)

    def test_validation_allow_mixed(self):
        # The validation succeed with a None value if the field allows mixed
        # state: True/False or None (unset).
        field = self.field_class('is-public', allow_mixed=True)
        with self.assert_not_raises(ValueError):
            field.validate(None)

    def test_validation_no_mixed_state(self):
        # The boolean field cannot be unset if mixed state is not allowed.
        field = self.field_class(
            'is-public', label='is public', allow_mixed=False)
        expected = 'the is public field requires a boolean value'
        with self.assert_value_error(expected):
            field.validate(None)


class TestUnexpectedField(FieldTestsMixin, unittest.TestCase):

    field_class = fields.UnexpectedField

    def assert_normalized(self, normalized_value, input_value):
        """Ensure the expected normalized value is returned."""
        field = self.field_class('last-name')
        self.assertEqual(normalized_value, field.normalize(input_value))

    def test_attributes(self):
        # The field attributes are properly stored in the field instance.
        field = self.field_class(
            'first-name', label='first name', help='your first name')
        self.assertEqual('first-name', field.name)
        self.assertEqual('first name', field.label)
        self.assertEqual('your first name', field.help)

    def test_default_attributes(self):
        # Only the name identifier is required when instantiating a field.
        field = self.field_class('last-name')
        self.assertEqual('last-name', field.name)
        self.assertEqual('last-name', field.label)
        self.assertEqual(
            'this field is unrecognized and can be safely removed', field.help)
        self.assertIsNone(field.default)
        self.assertFalse(field.required)
        self.assertFalse(field.readonly)

    def test_normalize_boolean(self):
        # The normalized boolean value is the value itself.
        self.assert_normalized(True, True)
        self.assert_normalized(False, False)

    def test_normalize_integer(self):
        # The normalized numeric value is the number itself.
        self.assert_normalized(42, 42)

    def test_normalize_none(self):
        # None normalization returns None.
        self.assert_normalized(None, None)

    def test_normalize_string_guess(self):
        # A string value is converted to the underlying type if possible.
        self.assert_normalized(42, '42')
        self.assert_normalized(47, ' 47 ')
        self.assert_normalized(True, 'true')
        self.assert_normalized(False, '\tFALSE\n')

    def test_normalize_string(self):
        # The normalization process returns the stripped value if the value is
        # a string.
        self.assert_normalized('a string', 'a string')
        self.assert_normalized('stripped', '\n stripped\t')

    def test_normalize_empty_string(self):
        # An empty string is normalized to None.
        self.assert_normalized(None, '')
        self.assert_normalized(None, ' ')

    def test_normalize_unknown(self):
        # The normalization process converts to string unrecognized values.
        self.assert_normalized('42.47', 42.47)
        self.assert_normalized('{}', {})

    def test_validate(self):
        # Unexpected values are always valid.
        field = self.field_class('last-name')
        for value in (None, 42, 42.47, True, False, 'a string'):
            with self.assert_not_raises(ValueError, value):
                field.validate(value)


class TestAutoGeneratedStringField(TestStringField):

    field_class = fields.AutoGeneratedStringField

    def test_generate(self):
        # The autogenerated field can generate random values.
        field = self.field_class('auto')
        value1 = field.generate()
        value2 = field.generate()
        # The generated values are unicode strings.
        self.assertIsInstance(value1, unicode)
        self.assertIsInstance(value2, unicode)
        # The generated values are not empty.
        self.assertNotEqual(0, len(value1))
        self.assertNotEqual(0, len(value2))
        # The generated values are different to each other.
        self.assertNotEqual(value1, value2)


class TestChoiceField(TestStringField):

    field_class = fields.ChoiceField
    choices = ('these', 'are', 'the', 'voyages')

    def test_validation_success(self):
        # No errors are raised if the value is included in the choices.
        field = self.field_class('word', choices=self.choices)
        for value in self.choices:
            with self.assert_not_raises(ValueError, value):
                field.validate(value)

    def test_validation_error_not_in_choices(self):
        # A ValueError is raised by choice fields if the value is not included
        # in the specified choices.
        field = self.field_class(
            'word', choices=self.choices, label='selected word')
        expected = ('the selected word requires the value to be one of the '
                    'following: these, are, the, voyages')
        with self.assert_value_error(expected):
            field.validate('resistance is futile')

    def test_validation_with_default(self):
        # The validation succeeds if the value is unset but a default one is
        # available.
        field = self.field_class(
            'word', choices=self.choices, default='voyages', required=True)
        with self.assert_not_raises(ValueError):
            field.validate(None)


class TestFilePathField(TestStringField):

    field_class = fields.FilePathField

    def test_validation_success(self):
        # The validation succeeds if the value is set and the path exists.
        field = self.field_class('path')
        with self.assert_not_raises(ValueError):
            field.validate(unicode(__file__))

    def test_validation_expanduser(self):
        # The ~ construct is properly expanded.
        field = self.field_class('path')
        basename, filename = os.path.split(unicode(__file__))
        with self.assert_not_raises(ValueError):
            with mock.patch('os.environ', {'HOME': basename}):
                field.validate('~/{}'.format(filename))

    def test_validation_error_file_not_found(self):
        # A ValueError is raised if the path does not exist.
        field = self.field_class('path')
        with self.assert_value_error('file not found in the specified path'):
            field.validate('__no-such-file__')

    def test_validation_error_directory(self):
        # A ValueError is raised if the path is a directory.
        field = self.field_class('path')
        with self.assert_value_error('file not found in the specified path'):
            field.validate('/tmp')


class TestSuggestionsStringField(TestStringField):

    field_class = fields.SuggestionsStringField

    def test_suggestions(self):
        # Suggested values are properly stored as a field attribute.
        suggestions = ('these', 'are', 'the', 'voyages')
        field = self.field_class(
            'word', suggestions=suggestions, label='selected word')
        self.assertEqual(suggestions, field.suggestions)


class TestPasswordField(TestStringField):

    field_class = fields.PasswordField

    def test_display(self):
        # A placeholder value is displayed.
        field = self.field_class('passwd')
        for value in (42, True, 'a unicode string'):
            self.assertEqual('*****', field.display(value), value)

    def test_display_bytes(self):
        # A placeholder value is still displayed.
        snowman = b'Here is a snowman\xc2\xa1: \xe2\x98\x83'
        field = self.field_class('passwd')
        self.assertEqual('*****', field.display(snowman))

    def test_display_no_values(self):
        # Do not display the placeholder if the value is not set.
        field = self.field_class('passwd')
        for value in (None, False, ''):
            self.assertEqual('None', field.display(value), value)


class TestAutoGeneratedPasswordField(
        TestAutoGeneratedStringField, TestPasswordField):

    field_class = fields.AutoGeneratedPasswordField
