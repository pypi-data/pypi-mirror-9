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

"""Tests for the Juju Quickstart CLI parameters implementation."""

from __future__ import unicode_literals

import unittest

from quickstart.cli import params
from quickstart.models import envs
from quickstart.tests import helpers


class TestParams(unittest.TestCase):

    def setUp(self):
        # Store parameters.
        self.env_type_db = envs.get_env_type_db()
        self.env_db = helpers.make_env_db()
        self.jenv_db = helpers.make_jenv_db()
        self.save_callable = lambda env_db: None
        self.remove_jenv_callable = lambda env_db: None
        # Set up a params object used in tests.
        self.params = params.Params(
            env_type_db=self.env_type_db,
            env_db=self.env_db,
            jenv_db=self.jenv_db,
            save_callable=self.save_callable,
            remove_jenv_callable=self.remove_jenv_callable,
        )

    def test_tuple(self):
        # The params object can be used as a tuple.
        env_type_db, env_db, jenv_db, save, remove = self.params
        self.assertIs(self.env_type_db, env_type_db)
        self.assertIs(self.env_db, env_db)
        self.assertIs(self.jenv_db, jenv_db)
        self.assertIs(self.save_callable, save)
        self.assertIs(self.remove_jenv_callable, remove)

    def test_attributes(self):
        # Parameters can be accessed as attributes.
        self.assertIs(self.env_type_db, self.params.env_type_db)
        self.assertIs(self.env_db, self.params.env_db)
        self.assertIs(self.jenv_db, self.params.jenv_db)
        self.assertIs(self.save_callable, self.params.save_callable)
        self.assertIs(
            self.remove_jenv_callable, self.params.remove_jenv_callable)

    def test_immutable(self):
        # It is not possible to replace a stored parameter.
        with self.assertRaises(AttributeError):
            self.params.env_db = {}

    def test_copy(self):
        # Params can be copied.
        params = self.params.copy()
        # The original object is not mutated by the copy.
        self.assertIs(self.env_type_db, self.params.env_type_db)
        self.assertIs(self.env_db, self.params.env_db)
        self.assertIs(self.jenv_db, self.params.jenv_db)
        self.assertIs(self.save_callable, self.params.save_callable)
        self.assertIs(
            self.remove_jenv_callable, self.params.remove_jenv_callable)
        # The new params object stores the same data.
        self.assertEqual(self.params, params)
        # But they do not refer to the same object.
        self.assertIsNot(self.params, params)

    def test_copy_mutations(self):
        # Internal mutable objects can be still mutated.
        params = self.params.copy()
        # Mutate the copy.
        params.env_db['environments']['lxc'] = {}
        # The mutation took effect.
        self.assertNotEqual(self.env_db, params.env_db)
        # The original object is still preserved.
        self.assertIs(self.env_db, self.params.env_db)
        # The two now store different data.
        self.assertNotEqual(self.params, params)
