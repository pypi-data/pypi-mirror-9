Juju Quickstart
===============

Juju Quickstart is a Juju plugin which allows for easily setting up a Juju
environment in very few steps. The environment is bootstrapped and set up so
that it can be managed using a Web interface (the Juju GUI).

Bundle deployments are also supported, and allow for setting up a complete
topology of services in one simple command.

Creating a development environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The development environment is created in a virtualenv. The environment
creation requires the *make*, *pip* and *virtualenv* programs to be installed.
To do that, run the following::

    $ make sysdeps

At this point, from the root of this branch, run the command::

    $ make

This command will create a ``.venv`` directory in the branch root, ignored
by DVCSes, containing the development virtual environment with all the
dependencies.

Testing and debugging the application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the tests::

    $ make test

Run the tests and lint/pep8 checks::

    $ make check

Display help about all the available make targets, including instructions on
setting up and running the application in the development environment::

    $ make help

Installing the application
~~~~~~~~~~~~~~~~~~~~~~~~~~

To install Juju Quickstart in your local system, run the following::

    $ sudo make install

This command will take care of installing the requirements and the application
itself.

Running the application
~~~~~~~~~~~~~~~~~~~~~~~

juju-core will recognize Juju Quickstart as a plugin once the application is
installed by the command above. At this point, the application can be started
by running ``juju quickstart``.

Run the following for the list of all available options::

    $ juju quickstart --help

Assuming a Juju environment named ``local`` is properly configured in your
``~/.juju/environments.yaml`` file, here is an example invocation::

    $ juju quickstart -e local

If you have not installed the application using ``sudo make install``, as
described above, you can run it locally using the virtualenv's Python
installation::

    $ .venv/bin/python juju-quickstart --help

Project structure
~~~~~~~~~~~~~~~~~

Juju Quickstart is a Python project. Source files can be found in the
``quickstart`` Python package included in this distribution.

A brief  description of the project structure follows, including the goals of
each module in the ``quickstart`` package.

* ``manage.py`` includes the main entry points for the ``juju-quickstart``
  command. Specifically:
  * ``manage.setup`` is used to set up the command line parser, the logging
    infrastructure and the interactive session (if required);
  * ``manage.run`` executes the application with the given options.

* ``app.py`` defines the main application functions, like bootstrapping an
  environment, deploying the Juju GUI or watching the deployment progress.
  The ``app.ProgramExit`` error can only be raised by functions in this module,
  and it causes the immediate exit (with an error) from the application.

The ``manage.py`` and ``app.py`` modules must be considered ``juju-quickstart``
execution specific: for this reason those modules are unlikely to be used as
libraries. All the other packages/modules in the application (except for views,
see below), should only include library-like code that can be reused in
different places by either Juju Quickstart or external programs.

* ``setting.py`` includes the application settings. Those must be considered as
  constant values to be reused throughout the application. The settings module
  should not import other ``quickstart`` modules.

* ``utils.py`` defines general purpose helper functions: when writing such
  utility objects it is likely that this is the right place where they should
  live. Separate modules are created when a set of utilities are related each
  other: this is the case, for instance, of ``serializers.py`` (YAML/JSON
  serialization utilities), ``ssh.py`` (SSH protocol related functions),
  ``platform_support.py`` etc.

* ``juju.py`` defines the WebSocket API client used by Juju Quickstart to
  connect to the Juju API server.

* the ``models`` package includes a module for each application model. Models
  are abstractions representing the data and information managed by Juju
  Quickstart, e.g. environment files, jenv files or charms. In the
  implementation of models, an effort has been made to use simple data
  structures in order to represent entities/objects, and composable functions
  to manipulate this information.

* the ``cli`` package contains the command line interactive session handling.
  Juju Quickstart uses Urwid to implement an ncurses-like interactive session:
  Urwid code must only live in the ``cli`` package.

That said, module docstrings often describe the goals and usage of each part of
the code: go have a look!

Pre-release QA
~~~~~~~~~~~~~~

The general steps for manual QA (until we get a continuous integration set up
with functional tests) should be run on trusty, utopic and vivid.

* Ensure juju-quickstart is installed from the juju-gui/quickstart-beta PPA.::

    sudo add-apt-repository ppa:juju-gui/quickstart-beta
    sudo apt update
    sudo apt install juju-quickstart

* Remove juju from the system.::

    sudo apt-get remove --purge juju-core

* Verify LXC environments can boot from scratch, using a local bundle::

    mkdir $HOME/bundles
    bzr branch lp:~charmers/charms/bundles/mediawiki/bundle $HOME/bundles/mediawiki
    juju-quickstart -e local -n single $HOME/bundles/mediawiki
    juju destroy-environment local -y

* Verify an environment that has already been bootstrapped is recogized and
  the GUI is deployed.  This test also shows that a remote bundle is properly
  deployed
::

    juju bootstrap -e local
    juju quickstart -e local bundle:mediawiki/single
    juju destroy-environment local -y

* Prove that an environments.yaml file can be created and used::

    # Temporarily move the .juju directory out of the way.
    mv ~/.juju ~/.juju-saved

    # Run quickstart and select the first option:
    juju quickstart

    # Ensure the GUI deploys properly and ~/.juju/environments.yaml looks
    # reasonable.

    juju destroy-environment local -y

    # Delete the data in the generated directory and restore the original
    rm -rf ~/.juju
    mv ~/.juju-saved ~/.juju

Repeat above on ec2.

Creating PPA releases
~~~~~~~~~~~~~~~~~~~~~

Due to an inconsistency of package names for the websocket package introduced
with trusty, the juju-quickstart packaging must be handled separately for
series before trusty and trusty and later.  Consequently, there are two
packaging branches and two build recipes.  The two packaging branches are:

* lp:juju-quickstart/packaging, and
* lp:juju-quickstart/packaging-pre-trusty

For the following instructions we'll use the -trunk version but the procedure
is the same for the -pre-trusty branch.

The packaging repository (including the ``debian`` directory) can be checked
out from lp:juju-quickstart/packaging, e.g.::

    $ bzr branch lp:juju-quickstart/packaging packaging
    $ cd packaging

Check that the packaging version reflects the latest Quickstart version. The
packaging version can be found in the ``debian/changelog`` file present in the
packaging branch root. To print the version of the current Quickstart, from the
juju-quickstart branch root, run the following::

    $ .venv/bin/python juju-quickstart --version

If the ``debian/changelog`` file is outdated, install the ``devscripts``
package and use ``dch`` to update the changelog, e.g.::

    $ sudo apt-get install devscripts
    $ dch -i  # Executed from the packaging branch root.

At this point, edit the changelog as required, commit and push the changes back
to the packaging branch trunk, and follow the instructions below.

The procedure is analogous for pre-trusty series releases, just using the
other packaging branch.

The recipe for creating packages for trusty and beyond is at
`juju-quickstart-trunk-daily
<https://code.launchpad.net/~juju-gui-charmers/+recipe/juju-quickstart-trunk-daily>`_.

The pre-trusty recipe is `juju-quickstart-pre-trusty-daily
<https://code.launchpad.net/~juju-gui-charmers/+recipe/juju-quickstart-pre-trusty-daily>`_.

We currently publish beta releases on the `Juju Quickstart Beta PPA
<https://launchpad.net/~juju-gui/+archive/quickstart-beta/+packages>`_.
When a beta release is ready to be published, we move over the packages from
the Juju Quickstart Beta PPA to the `Juju stable PPA
<https://launchpad.net/~juju/+archive/stable>`_.

Packages depend on `python-jujuclient` and `python-websocket-client` to be
available. They are available in trusty and later, and they are also stored in
our PPA in order to support previous Ubuntu releases.  Note we depend on
version 0.12.0 of python-websocket and that version is in the PPAs.

Creating PyPI releases
~~~~~~~~~~~~~~~~~~~~~~

Juju Quickstart is present on `PyPI
<https://pypi.python.org/pypi/juju-quickstart>`_.
It is possible to register and upload a new release on PyPI by just running
``make release`` and providing your PyPI credentials.  Note there are no
series-specific changes required for publishing to PyPI.

Creating a Homebrew release
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The brew formula fetches its source from PyPI, so it must be done after the PyPI
release.

1. Start with a fresh brew::

    $ brew update

#. Go to PyPI (https://pypi.python.org/pypi/juju-quickstart) and download the
   new tgz file.

#. Verify the md5 checksum matches that on the PyPI site via, e.g. ::

    $ md5 ~/Downloads/juju-quickstart-1.4.0.tar.gz

#. Use brew to edit the juju-quickstart formula::

    $ brew edit juju-quickstart

#. Update the URL to point to the new release tar.gz file.

#. Compute the SHA1 checksum for the tgz and insert it as the JujuQuickstart
   sha1 value::

    $ shasum ~/Downloads/juju-quickstart-1.4.0.tar.gz

#. Test the new formula by upgrading juju-quickstart (errors about bottle
   download failures are acceptable)::

    $ brew upgrade juju-quickstart

#. Run the formula test::

    $ brew test juju-quickstart

#. Perform full QA as above.

After successful QA, follow the procedure outlined in the Homebrew
`Formula-Cookbook
<https://github.com/Homebrew/homebrew/wiki/Formula-Cookbook#commit>`_. The
project is adamant about having one file and one commit per pull request.
Rebase and squash commits if required.

1. Move to the brew git directory::

    $ cd `brew --repository`

#. Create a new branch, add the changed file, and commit::

    $ git checkout -b juju-quickstart-1.4.0
    $ git add Library/Formula/juju-quickstart.rb
    $ git commit -a -m "juju-quickstart 1.4.0"
    $ git push git@github.com:juju/homebrew.git juju-quickstart-1.4.0

#. Go to https://github.com/juju/homebrew to create a pull request.
#. Copy the debian/changelog from the lp:juju-quickstart/packaging as the pull
   request comment.  Keep the name simple, e.g. 'juju-quickstart 1.4.0'.
#. Watch the pull request and ensure it passes Jenkins.  If changes must be made,
   rebase the branch and squash commits before pushing.
#. If the branch makes it through CI without errors it will be accepted and
   merged without human intervention. A recent branch took about two hours
   from the time the pull request was made.

Tagging a new release
~~~~~~~~~~~~~~~~~~~~~

When a new release is successfully done (meaning it passed the QA described
above and has been correctly published on PyPI, the PPAs and Homebrew), it is
time to tag it for future reference. To do that, just run the following
commands on the trunk branch of Juju Quickstart::

  $ bzr tag {version} # For instance bzr tag "1.6.0"
  $ bzr push :parent

Updating application and test dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test dependencies are listed in the ``test-requirements.pip`` file in the
branch root, application ones in the ``requirements.pip`` file. The former
includes the latter, so any updates to the application requirements will also
update the test dependencies and therefore the testing virtual environment.
Note that, since the source requirements are dynamically generated parsing
``requirements.pip``, that file must only include ``PACKAGE==VERSION`` formatted
dependencies, and not other pip specific requirement specifications.

Also ensure, before updating the application dependencies, that those packages
are available in the main Ubuntu repositories for the series we support (from
precise to vivid), or in the `Juju Quickstart Beta PPA
<https://launchpad.net/~juju-gui/+archive/quickstart-beta/+packages>`_.

Please also keep up to date the possible values for the environments.yaml
default-series field (see ``quickstart.settings.JUJU_DEFAULT_SERIES``) and the
set of series supported by the Juju GUI charm
(see ``quickstart.settings.JUJU_GUI_SUPPORTED_SERIES``).

Debugging bundle support
~~~~~~~~~~~~~~~~~~~~~~~~

When deploying a bundle, Quickstart just start the import process sending an
API request to the GUI charm builtin server, and then lets the user observe
the deployment process using the GUI.

Under the hood, a bundle deployment is executed by the GUI builtin server,
which in turn leverages the juju-deployer library. Since juju-deployer is not
asynchronous, the actual deployment is executed in a separate process.

Sometimes, when an error occurs, it is not obvious where to retrieve
information about what is going on. The GUI builtin server exposes some bundle
information in two places:

- ``https://<juju-gui-url>/gui-server-info`` displays in JSON format the current
  status of all scheduled/started/completed bundle deployments;
- ``/var/log/upstart/guiserver.log`` is the builtin server log file, which includes
  logs output from the juju-deployer library.

Moreover, setting ``builtin-server-logging=debug`` gives more debugging
information, e.g. it prints to the log the contents of the WebSocket messages
sent by the client (usually the Juju GUI) and by the Juju API server.
As mentioned, juju-deployer works on its own sandbox and uses its own API
connections, and for this reason the WebSocket traffic it generates is not
logged.

Sometimes, while debugging, it is convenient to restart the builtin server
(which also empties the bundle deployments queue). To do that, run the
following in the Juju GUI machine::

    $ service guiserver restart
