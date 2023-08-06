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

"""Juju Quickstart platform management."""

from __future__ import (
    print_function,
    unicode_literals,
)

import logging
import os
import platform

from quickstart import (
    settings,
    utils,
)


def validate_platform(pf):
    """Validate the platform is supported and has the required files installed.

    Raises ValueError if validation fails.
    Otherwise returns None.
    """
    unsupported_messages = {
        settings.LINUX_UNKNOWN: 'unsupported Linux without apt-get nor rpm',
        settings.LINUX_RPM: 'juju-quickstart on RPM-based Linux is not yet' +
                            ' supported',
        settings.WINDOWS: 'juju-quickstart on Windows is not yet supported',
        settings.UNKNOWN_PLATFORM: 'unable to determine the OS platform',
    }

    error_msg = unsupported_messages.get(pf)
    if error_msg is not None:
        raise ValueError(error_msg.encode('utf-8'))
    elif pf == settings.OSX and not os.path.isfile('/usr/local/bin/brew'):
        raise ValueError(
            b'juju-quickstart requires brew to be installed on OS X. '
            b'To install brew, see http://brew.sh')


def get_platform():
    """Return the platform of the host."""
    system = platform.system()
    if system == 'Darwin':
        return settings.OSX
    elif system == 'Windows':
        return settings.WINDOWS
    elif system == 'Linux':
        if os.path.isfile('/usr/bin/apt-get'):
            return settings.LINUX_APT
        elif os.path.isfile('/usr/bin/rpm'):
            return settings.LINUX_RPM
        else:
            return settings.LINUX_UNKNOWN
    else:
        return settings.UNKNOWN_PLATFORM


def _installer_apt(distro_only, required_packages):
    """Perform package installation on Linux with apt.

    Raises OSError if the called functions raise it or an error is
    encountered.
    """
    if not distro_only:
        utils.add_apt_repository('ppa:juju/stable')
    print('sudo privileges will be used for the installation of \n'
          'the following packages: {}\n'
          'this can take a while...'.format(', '.join(required_packages)))
    retcode, _, error = utils.call(
        'sudo', '/usr/bin/apt-get', 'install', '-y', *required_packages)
    if retcode:
        raise OSError(bytes(error))


def _installer_osx(distro_only, required_packages):
    """Perform package installation on OS X via brew.

    Note distro_only is meaningless on OS X as there is no PPA option.  It is
    silently ignored.
    Raises OSError if the called functions raise it or an error is
    encountered.
    """
    print('Installing the following packages: {}\n'.format(
        ', '.join(required_packages)))
    retcode, _, error = utils.call(
        '/usr/local/bin/brew', 'install', *required_packages)
    if retcode:
        raise OSError(bytes(error))


INSTALLERS = {
    settings.LINUX_APT: _installer_apt,
    settings.OSX: _installer_osx,
}


def get_juju_command(platform):
    """Return the path to the Juju command on the given platform.

    Also return a flag indicating whether the user requested to customize
    the Juju command by providing a JUJU environment variable.

    If the platform does not have a novel location, the default will be
    returned.

    If the environment variable JUJU is set, then its value will be
    returned.
    """
    juju_command = os.getenv('JUJU', '').strip()
    platform_command = settings.JUJU_CMD_PATHS.get(
        platform,
        settings.JUJU_CMD_PATHS['default'])
    if juju_command and juju_command != platform_command:
        logging.warn("a customized juju is being used")
        return juju_command, True
    return platform_command, False


def get_juju_installer(platform):
    """Return the installer for the host platform.

    Returns installer callable.
    Raises ValueError if a platform we don't support is detected.
    """
    installer = INSTALLERS.get(platform)
    if installer is None:
        raise ValueError(b'No installer found for host platform.')
    return installer


def supports_local(platform):
    """Return True if the platform supports local (LXC) deploys."""
    return platform in (settings.LINUX_APT, settings.LINUX_RPM)
