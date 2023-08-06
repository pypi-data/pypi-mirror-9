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

"""Juju Quickstart functional tests package.

This package includes functional tests for Juju Quickstart.
In those tests, Juju Quickstart is run to bootstrap and deploy the Juju GUI
in a real Juju environment. For this reason, completing the suite takes a
while. Therefore tests are disabled by default, and are intended to be only run
before releasing a new version of the application.

To run the tests, set the JUJU_QUICKSTART_FTESTS environment variable to "1",
or use "make ftest/fcheck".

Functional tests require:
- a Juju home correctly set up with at least one environment defined in the
  environments.yaml file;
- SSH keys already generated for the user running the tests;
- a working Internet connection.

By default, the current default environment is used to run the application.
To change the environment, set the JUJU_ENV environment variable, e.g.:

    make fcheck JUJU_ENV=myenv

Also note that when running functional tests against a local environment, the
password for sudo privileges may be asked while the suite is run.
"""
