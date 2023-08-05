Juju Quickstart
===============

Juju Quickstart is an opinionated command-line tool that quickly starts Juju
and the GUI, whether you've never installed Juju or you have an existing Juju
environment running.

Features include the following:

* New users are guided, as needed, to install Juju, set up SSH keys, and
  configure it for first use.
* Juju environments can be created and managed from a command line interactive
  session.
* The Juju GUI is automatically installed, adding no additional machines
  (installing on an existing state server when possible).
* Bundles can be deployed, from local files, HTTP(S) URLs, or the charm store,
  so that a complete topology of services can be set up in one simple command.
* Quickstart ends by opening the browser and automatically logging the user
  into the GUI, to observe and manage the environment visually.
* Users with a running Juju environment can run the quickstart command again to
  simply re-open the GUI without having to find the proper URL and password.

To start Juju Quickstart, run the following::

    juju-quickstart [-i]

Run ``juju-quickstart -h`` for a list of all the available options.

Once Juju has been installed, the command can also be run as a juju plugin,
without the hyphen (``juju quickstart``).


Supported Versions
------------------

Juju Quickstart is available on Ubuntu releases 12.04 LTS (precise), 14.04 LTS
(trusty), 14.10 (utopic), 15.04 (vivid) and on OS X (10.7 and later).

Starting from version 1.5.0, Juju Quickstart only supports Juju >= 1.18.1.

Ubuntu Installation
~~~~~~~~~~~~~~~~~~~

For installation on precise you'll need to enable the Juju PPA by first
executing::

  sudo add-apt-repository ppa:juju/stable
  sudo apt-get update
  sudo apt-get install juju-quickstart

For trusty and above the PPA is not required and you simply need to install it
with::

  sudo apt-get install juju-quickstart

Alternatively you may install Juju Quickstart via pip with::

  pip install juju-quickstart

OS X Installation
~~~~~~~~~~~~~~~~~

You may install Juju Quickstart via Homebrew or pip.  See http://brew.sh for
instructions on installing Homebrew.

To install Quickstart via Homebrew do the following::

    brew install juju-quickstart

You may also install via pip. Note that you'll still need to have Homebrew
installed even if you use pip, because it is required to install Juju itself.
To install via pip do::

    pip install juju-quickstart
