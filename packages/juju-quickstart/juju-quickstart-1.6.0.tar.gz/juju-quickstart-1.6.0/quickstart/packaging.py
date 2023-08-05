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

"""Juju Quickstart packaging configuration.

This module is parsed and modified in the process of packaging quickstart
for Ubuntu distributions.

DO NOT MODIFY this file without informing server/distro developers.
"""

# The source from where to install juju-core packages.
# Possible values are:
#   - ppa: the Juju stable packages PPA. This value is usually set in the code
#     base and PyPI releases;
#   - distro: the distribution repository. This value is usually set in the deb
#     releases included in the Ubuntu repositories.
JUJU_SOURCE = 'ppa'
