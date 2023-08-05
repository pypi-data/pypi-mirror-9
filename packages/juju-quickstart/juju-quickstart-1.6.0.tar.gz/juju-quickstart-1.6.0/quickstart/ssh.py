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

"""Juju Quickstart SSH management functions."""

from __future__ import (
    print_function,
    unicode_literals,
)

import re
import os
import sys
import time

from quickstart import utils


def check_keys():
    """Check whether or not ssh keys exist and are loaded by the agent.

    Raise an OSError if we can't load the keys because they're broken in some
    way.

    Return true if there are ssh identities loaded and available in an agent,
    false otherwise.
    """
    no_keys_msg = 'The agent has no identities.\n'
    retcode, output, _ = utils.call('/usr/bin/ssh-add', '-l')
    if retcode == 0:
        # We have keys and an agent.
        return True
    elif retcode == 1 and output == no_keys_msg:
        # We have an agent, but no keys currently loaded.
        retcode, output, error = utils.call('/usr/bin/ssh-add')
        if retcode == 0:
            # We were able to load an identity
            return True
        elif retcode == 1:
            # If ssh-add is called without -l and there are no identities
            # available, there will be no output or error, but retcode will
            # still be 1.
            return False
        else:
            # We weren't able to load keys for some other reason, such as being
            # readable by group or world, or malformed.
            msg = 'error attempting to add ssh keys: {}'.format(error)
            raise OSError(msg.encode('utf-8'))
    return False


def create_keys():
    """Create SSH keys for the user.

    Raises an OSError if the keys were not created successfully.

    NB: this involves user interaction for entering the passphrase; this may
    have to change if creating SSH keys takes place in the urwid interface.
    """
    key_file = os.path.join(os.path.expanduser('~'), '.ssh', 'id_rsa')
    print('generating new ssh key...')
    retcode, _, error = utils.call('/usr/bin/ssh-keygen',
                                   '-q',  # silent
                                   '-b', '4096',  # 4096 bytes
                                   '-t', 'rsa',  # RSA type
                                   '-C', 'Generated with Juju Quickstart',
                                   '-f', key_file)
    if retcode:
        msg = 'error generating ssh key: {}'.format(error)
        raise OSError(msg.encode('utf-8'))
    print('adding key to ssh-agent...')
    retcode, _, error = utils.call('/usr/bin/ssh-add')
    if retcode:
        msg = 'error adding key to agent: {}'.format(error)
        raise OSError(msg.encode('utf-8'))
    print('a new ssh key was generated in {}'.format(key_file))


def start_agent():
    """Start an ssh-agent and propagate its environment variables."""
    retcode, output, error = utils.call('/usr/bin/ssh-agent')
    if retcode:
        raise OSError(error.encode('utf-8'))
    os.putenv('SSH_AUTH_SOCK',
              re.search('SSH_AUTH_SOCK=([^;]+);', output).group(1))
    os.putenv('SSH_AGENT_PID',
              re.search('SSH_AGENT_PID=([^;]+);', output).group(1))
    print('ssh-agent has been started.\n'
          'To interact with Juju or quickstart again after quickstart\n'
          'finishes, please run the following in a terminal to start '
          'ssh-agent:\n  eval `ssh-agent`\n')


def watch_for_keys():
    """Watch for generation of ssh keys from another terminal or window.

    Raise an OSError if an error occurs while checking for SSH keys.

    This will run until keys become visible to quickstart or killed by the
    user.
    """
    print('Please run this command in another terminal or window and follow\n'
          'the instructions it produces; quickstart will continue when keys\n'
          'are generated, or ^C to quit.\n\n'
          '  ssh-keygen -b 4096 -t rsa\n\nWaiting...')
    try:
        while not check_keys():
            # Print and flush the buffer immediately; an empty end kwarg will
            # not cause the buffer to flush until after a certain number of
            # bytes.
            print('.', end='')
            sys.stdout.flush()
            time.sleep(3)
    except KeyboardInterrupt:
        sys.exit(b'\nquitting')
