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

"""Juju Quickstart view parameters implementation.

This module contains an implementation of a composite parameter object to be
used in views.

The Params named tuple is intended to both help grouping view parameters
together and avoid undesired mutations, by allowing explicit copies of the
whole parameters object (see the Params.copy instance method).
"""

from __future__ import unicode_literals

from collections import namedtuple
import copy


_PARAMS = (
    'env_type_db',
    'env_db',
    'jenv_db',
    'save_callable',
    'remove_jenv_callable',
)


class Params(namedtuple('Params', _PARAMS)):
    """View parameters as a named tuple."""

    # Define empty slots to keep memory requirements low by preventing the
    # creation of instance dictionaries.
    # See https://docs.python.org/2/library/collections.html
    __slots__ = ()

    def copy(self):
        """Return a deep copy of the stored parameters."""
        return self.__class__(
            env_type_db=self.env_type_db,
            env_db=copy.deepcopy(self.env_db),
            jenv_db=copy.deepcopy(self.jenv_db),
            save_callable=self.save_callable,
            remove_jenv_callable=self.remove_jenv_callable,
        )
