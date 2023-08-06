# This file is part of the Juju Quickstart Plugin, which lets users set up a
# Juju environment in very few steps (https://launchpad.net/juju-quickstart).
# Copyright (C) 2013-2014 Canonical Ltd.
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

"""Juju Quickstart application management."""

from __future__ import (
    print_function,
    unicode_literals,
)

import argparse
import logging
import os
import shutil
import sys
import webbrowser

import quickstart
from quickstart import (
    app,
    jujutools,
    packaging,
    platform_support,
    settings,
    utils,
)
from quickstart.cli import (
    params,
    views,
)
from quickstart.models import (
    bundles,
    envs,
    jenv,
    references,
)


version = quickstart.get_version()


class _DescriptionAction(argparse.Action):
    """A customized argparse action that just shows a description."""

    def __call__(self, parser, *args, **kwargs):
        print(settings.DESCRIPTION)
        parser.exit()


def _get_packaging_info(juju_source, platform):
    """Return packaging info based on the given juju source.

    The juju_source argument can be either "ppa" or "distro".

    Packaging info is a tuple containing:
        - distro_only: whether to install juju-core packages from the distro
          repositories or the external PPA;
        - distro_only_help: the help text for the --distro-only flag;
        - ppa_help: the help text for the --ppa flag.
    """
    if platform == settings.LINUX_APT:
        distro_only_help = ('Do not use external sources when installing and '
                            'setting up Juju')
        ppa_help = 'Use external sources when installing and setting up Juju'
        disable_help = '\n(enabled by default, use {} to disable)'
        if juju_source == 'distro':
            distro_only = True
            distro_only_help += disable_help.format('--ppa')
        else:
            distro_only = False
            ppa_help += disable_help.format('--distro-only')
    else:
        # If not LINUX_APT then distro_only and ppa make no sense.  Prevent
        # the user from seeing them but allow reasonable values in options.
        distro_only = True
        distro_only_help = argparse.SUPPRESS
        ppa_help = argparse.SUPPRESS
    return distro_only, distro_only_help, ppa_help


def _validate_bundle(options, parser):
    """Validate and process the bundle options.

    Populate the options namespace with the following names:
        - bundle: the bundle object as an instance of
          "quickstart.models.bundles.Bundle";

    Exit with an error if the bundle options are not valid, or if the bundle
    content cannot be retrieved.
    """
    try:
        options.bundle = bundles.from_source(
            options.bundle_source, options.bundle_name)
    except (IOError, ValueError) as err:
        return parser.error(b'unable to open the bundle: {}'.format(err))


def _validate_charm_url(options, parser):
    """Validate the provided charm URL option.

    Exit with an error if:
        - the URL is not a valid charm URL;
        - the URL represents a local charm;
        - the charm series is not supported;
        - a bundle deployment has been requested but the provided charm does
          not support bundles.

    Leave the options namespace untouched.
    """
    try:
        ref = references.Reference.from_fully_qualified_url(options.charm_url)
    except ValueError as err:
        return parser.error(bytes(err))
    if ref.is_local():
        return parser.error(b'local charms are not allowed: {}'.format(ref))
    if ref.series not in settings.JUJU_GUI_SUPPORTED_SERIES:
        return parser.error('unsupported charm series: {}'.format(ref.series))
    if (
        # The user requested a bundle deployment.
        options.bundle_source is not None and
        # This is the official Juju GUI charm.
        ref.name == settings.JUJU_GUI_CHARM_NAME and not ref.user and
        # The charm at this revision does not support bundle deployments.
        ref.revision < settings.MINIMUM_REVISIONS_FOR_BUNDLES[ref.series]
    ):
        return parser.error(
            'bundle deployments not supported by the requested charm '
            'revision: {}'.format(ref))


def _retrieve_env_db(parser, env_file=None):
    """Retrieve the environment database (or create an in-memory empty one)."""
    if env_file is None:
        return envs.create_empty_env_db()
    try:
        return envs.load(env_file)
    except ValueError as err:
        return parser.error(bytes(err))


def _create_save_callable(parser, env_file):
    """Return a function that can be used to save an env_db to the env_file.

    The returned function is used as save_callable by the environments
    management views.

    The resulting function uses the given parser instance to exit the
    application with an error if an OSError exception is raised while saving
    the environments database.
    """
    backup_function = utils.run_once(shutil.copyfile)

    def save_callable(env_db):
        try:
            envs.save(env_file, env_db, backup_function=backup_function)
        except OSError as err:
            return parser.error(bytes(err))

    return save_callable


def _start_interactive_session(parser, env_type_db, env_db, jenv_db, env_file):
    """Start the Urwid interactive session.

    Return the env_data corresponding to the user selected environment.
    Exit the application if the user exits the interactive session without
    selecting an environment to start.
    """
    parameters = params.Params(
        env_type_db=env_type_db,
        env_db=env_db,
        jenv_db=jenv_db,
        save_callable=_create_save_callable(parser, env_file),
        remove_jenv_callable=jenv.remove,
    )
    new_env_db, env_data = views.show(views.env_index, parameters)
    if new_env_db != env_db:
        print('changes to the environments file have been saved')
    if env_data is None:
        # The user exited the interactive session without selecting an
        # environment to start: this means this was just an environment
        # editing session and we can just quit now.
        return sys.exit('quitting')
    return env_data


def _retrieve_env_data(parser, env_type_db, env_db, jenv_db, env_name):
    """Retrieve and return the env_data corresponding to the given env_name.

    Invoke a parser error if the environment does not exist or is not valid.
    """
    try:
        env_data = envs.get_env_data(env_db, env_name)
    except ValueError:
        # The specified environment does not exist in the environments file.
        # Check if this is an imported environment.
        try:
            return envs.get_env_data(jenv_db, env_name)
        except ValueError as err:
            # The environment cannot be found anywhere, exit with an error.
            return parser.error(bytes(err))
    # If the environment was found in the environments.yaml file, we can also
    # validate it.
    env_metadata = envs.get_env_metadata(env_type_db, env_data)
    errors = envs.validate(env_metadata, env_data)
    if errors:
        msg = 'cannot use the {} environment:\n{}'.format(
            env_name, '\n'.join(errors.values()))
        return parser.error(msg.encode('utf-8'))
    return env_data


def _setup_env(options, parser):
    """Set up, validate and process the provided environment related options.

    Also start the environments management interactive session if required.

    Exit with an error if options are not valid.
    """
    logging.debug('setting up juju environments')
    env_name = options.env_name
    env_file = os.path.abspath(os.path.expanduser(options.env_file))
    interactive = options.interactive
    env_file_exists = os.path.exists(env_file)
    if not env_file_exists:
        # If the Juju home is not set up, force the interactive mode and ignore
        # the user provided env name.
        interactive = True
        env_name = None
    # Validate the environment name.
    if env_name is None and not interactive:
        # The user forced non-interactive mode but a default env name cannot
        # be retrieved. In this case, just exit with an error.
        return parser.error(
            'unable to find an environment name to use\n'
            'It is possible to specify the environment to use by either:\n'
            '  - selecting one from the quickstart interactive session,\n'
            '    i.e. juju quickstart -i;\n'
            '  - passing the -e or --environment argument;\n'
            '  - setting the JUJU_ENV environment variable;\n'
            '  - using "juju switch" to select the default environment;\n'
            '  - setting the default environment in {}.'.format(env_file)
        )

    # Retrieve the environment database (or create an in-memory empty one).
    env_db = _retrieve_env_db(parser, env_file if env_file_exists else None)
    jenv_db = jenv.get_env_db()

    # Validate the environment.
    env_type_db = envs.get_env_type_db()
    if interactive:
        # Start the interactive session.
        env_data = _start_interactive_session(
            parser, env_type_db, env_db, jenv_db, env_file)
    else:
        # This is a non-interactive session and we need to validate the
        # selected environment before proceeding.
        env_data = _retrieve_env_data(
            parser, env_type_db, env_db, jenv_db, env_name)
    # Check for local support, if requested.
    options.env_type = env_data['type']
    no_local_support = not platform_support.supports_local(options.platform)
    if options.env_type == 'local' and no_local_support:
        return parser.error(
            'this host platform does not support local environments'
        )
    # Update the options namespace with the new values.
    options.env_file = env_file
    options.env_name = env_data['name']
    options.default_series = env_data.get('default-series')
    options.interactive = interactive


def _configure_logging(level):
    """Set up the application logging."""
    root = logging.getLogger()
    # Remove any previous handler on the root logger.
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    logging.basicConfig(
        level=level,
        format=(
            '%(asctime)s %(levelname)s '
            '%(module)s:%(lineno)d '
            '%(message)s'
        ),
        datefmt='%H:%M:%S',
    )


def _convert_options_to_unicode(options):
    """Convert all byte string values in the options namespace to unicode.

    Modify the options in place and return None.
    """
    encoding = sys.stdin.encoding or 'utf-8'
    for key, value in options._get_kwargs():
        if isinstance(value, bytes):
            setattr(options, key, value.decode(encoding))


def _validate_platform(parser, platform):
    """Validate the platform.
    Exit with an error if platform is not supported by quickstart or is
    missing files.
    """
    try:
        platform_support.validate_platform(platform)
    except ValueError as err:
        return parser.error(bytes(err))


def setup():
    """Set up the application options and logger.

    Return the options as a namespace containing the following attributes:
        - bundle_name: the optional name of the bundle in the case the legacy
          bundle format is being used, or None if the name is not specified;
        - bundle_source: the optional bundle identifier to be deployed, or None
          if a bundle deployment is not requested;
        - charm_url: the Juju GUI charm URL or None if not specified;
        - constraints: the environment constrains or None if not set;
        - debug: whether debug mode is activated;
        - distro_only: install Juju only using the distribution packages;
        - env_file: the absolute path of the Juju environments.yaml file;
        - env_name: the name of the Juju environment to use;
        - env_type: the provider type of the selected Juju environment;
        - interactive: whether to start the interactive session;
        - open_browser: whether the GUI browser must be opened;
        - platform: The host platform;
        - upload_tools: whether to upload local version of tools;
        - upload_series: the comma-separated series list for which tools will
          be uploaded, or None if not set.

    The following attributes will also be included in the namespace if a bundle
    deployment is requested:
        - bundle: the bundle instance to be deployed, as an instance of
          "quickstart.models.bundles.Bundle".

    Exit with an error if the provided arguments are not valid.
    """
    # Determine the host platform.  This needs to be done early as it affects
    # the options we present.
    platform = platform_support.get_platform()

    default_env_name = envs.get_default_env_name()
    default_distro_only, distro_only_help, ppa_help = _get_packaging_info(
        packaging.JUJU_SOURCE, platform)
    # Define the help message for the --environment option.
    env_help = 'The name of the Juju environment to use'
    if default_env_name is not None:
        env_help = '{} (%(default)s)'.format(env_help)
    # Create and set up the arguments parser.
    parser = argparse.ArgumentParser(
        description=quickstart.__doc__, epilog=quickstart.FEATURES,
        formatter_class=argparse.RawTextHelpFormatter)
    # Note: since we use the RawTextHelpFormatter, when adding/changing options
    # make sure the help text is nicely displayed on small 80 columns terms.
    parser.add_argument(
        'bundle_source', default=None, nargs='?', metavar='BUNDLE',
        help='The optional bundle to be deployed. The bundle can be:\n'
             '1) a bundle path as shown in jujucharms.com, e.g.\n'
             '   "mediawiki-single" or "django".\n'
             '   Non promulgated bundles can be requested providing\n'
             '   the user, e.g. "u/bigdata-dev/apache-analytics-sql".\n'
             '   A specific bundle revision can also be requested,\n'
             '   e.g. "mediawiki-scalable/7".\n'
             '   If not specified, the most recent revision is used;\n'
             '2) a jujucharms.com full URL of the bundle detail page,\n'
             '   with or without the revision. e.g.\n'
             '   "{jujucharms}mongodb-cluster/4" or\n'
             '   "{jujucharms}openstack";\n'
             '3) a URL ("http:" or "https:") to a YAML/JSON, e.g.\n'
             '   "https://raw.github.com/user/my/master/bundle.yaml";\n'
             '4) a local path to a YAML/JSON file with ".yaml" or\n'
             '   ".json" extension, e.g. "~/bundles/django.yaml";\n'
             '5) a legacy fully qualified bundle URL, starting with\n'
             '   "bundle:", e.g. "bundle:mediawiki/single".\n'
             '   Non promulgated bundles can be requested providing\n'
             '   the user, e.g. "bundle:~user/mediawiki/single".\n'
             '   A specific bundle revision can also be requested,\n'
             '   e.g. "bundle:~myuser/mediawiki/42/single".\n'
             '   If not specified, the last bundle revision is used.\n'
             '   Note that this form is DEPRECATED, and a deprecation\n'
             '   warning is printed suggesting the new value to use\n'
             ''.format(jujucharms=settings.JUJUCHARMS_URL))
    parser.add_argument(
        '-e', '--environment', default=default_env_name, dest='env_name',
        help=env_help)
    parser.add_argument(
        '-n', '--bundle-name', default=None, dest='bundle_name',
        help='The name of the bundle to use.\n'
             'This must be included in the provided bundle YAML/JSON.\n'
             'Specifying the bundle name is not required if the\n'
             'bundle YAML/JSON only contains one bundle. This option\n'
             'is ignored if the bundle file is not specified')
    parser.add_argument(
        '-i', '--interactive', action='store_true', dest='interactive',
        help='Start the environments management interactive session')
    parser.add_argument(
        '--environments-file', dest='env_file',
        default=os.path.join(settings.JUJU_HOME, 'environments.yaml'),
        help='The path to the Juju environments YAML file\n(%(default)s)')
    parser.add_argument(
        '--gui-charm-url', dest='charm_url',
        help='The Juju GUI charm URL to deploy in the environment.\n'
             'If not provided, the last release of the GUI will be\n'
             'deployed. The charm URL must include the charm version,\n'
             'e.g. "cs:~juju-gui/precise/juju-gui-162". This option is\n'
             'ignored if the GUI is already present in the environment')
    parser.add_argument(
        '--no-browser', action='store_false', dest='open_browser',
        help='Avoid opening the browser to the GUI at the end of the\nprocess')

    parser.add_argument(
        '--distro-only', action='store_true', dest='distro_only',
        default=default_distro_only, help=distro_only_help)
    parser.add_argument(
        '--ppa', action='store_false', dest='distro_only',
        default=not default_distro_only, help=ppa_help)
    parser.add_argument(
        '--version', action='version', version='%(prog)s {}'.format(version))
    parser.add_argument(
        '--debug', action='store_true',
        help='Turn debug mode on. When enabled, all the subcommands\n'
             'and API calls are logged to stdout, and the Juju\n'
             'environment is bootstrapped passing --debug')
    # This is required by juju-core: see "juju help plugins".
    parser.add_argument(
        '--description', action=_DescriptionAction, default=argparse.SUPPRESS,
        nargs=0, help="Show program's description and exit")
    # These options are passed to juju bootstrap.
    parser.add_argument(
        '--upload-tools', action='store_true',
        help='upload local version of tools before bootstrapping')
    parser.add_argument(
        '--upload-series',
        help='upload tools for supplied comma-separated series list')
    parser.add_argument(
        '--constraints',
        help='If constraints are specified, they will apply to the machine\n'
             'provisioned for the Juju state server. \n'
             'They will also be set as default constraints on the\n'
             'environment for all future machines, exactly as if the\n'
             'constraints were set with "juju set-constraints".\n')
    # Parse the provided arguments.
    options = parser.parse_args()

    # Set up logging.
    _configure_logging(logging.DEBUG if options.debug else logging.INFO)

    # Validate and add in the platform for convenience.
    _validate_platform(parser, platform)
    options.platform = platform

    # Convert the provided string arguments to unicode.
    _convert_options_to_unicode(options)
    # Validate and process the provided arguments.
    _setup_env(options, parser)
    if options.bundle_source is not None:
        _validate_bundle(options, parser)
    if options.charm_url is not None:
        _validate_charm_url(options, parser)
    return options


def run(options):
    """Run the application."""
    print('juju quickstart v{}'.format(version))
    if options.bundle_source is not None:
        print('contents loaded for {} (services: {})'.format(
            options.bundle, len(options.bundle.services())))

    juju_command, custom_juju = platform_support.get_juju_command(
        options.platform)

    logging.debug('ensuring juju and dependencies are installed')
    juju_version = app.ensure_dependencies(
        options.distro_only, options.platform, juju_command)
    app.check_juju_supported(juju_version)

    logging.debug('ensuring SSH keys are available')
    app.ensure_ssh_keys()

    # Bootstrap the Juju environment or reuse an already bootstrapped one.
    already_bootstrapped = True
    env_type = options.env_type
    api_address = app.check_bootstrapped(options.env_name)
    if api_address is None:
        print('bootstrapping the {} environment'.format(options.env_name))
        if env_type == 'local':
            # If this is a local environment, notify the user that "sudo" will
            # be required by Juju to bootstrap the environment.
            print('sudo privileges will be required to bootstrap the '
                  'environment')
        already_bootstrapped = app.bootstrap(
            options.env_name, juju_command,
            debug=options.debug,
            upload_tools=options.upload_tools,
            upload_series=options.upload_series,
            constraints=options.constraints)
    if already_bootstrapped:
        print('reusing the already bootstrapped {} environment'.format(
            options.env_name))

    # Retrieve the environment status, ensure it is in a ready state and
    # contextually fetch the bootstrap node series.
    print('retrieving the environment status')
    bootstrap_node_series = app.status(options.env_name, juju_command)

    # If the environment was not already bootstrapped, we need to retrieve
    # the API address.
    if api_address is None:
        print('retrieving the Juju API address')
        api_address = app.get_api_address(options.env_name, juju_command)

    # Retrieve the Juju environment unique identifier.
    env_uuid = app.get_env_uuid_or_none(options.env_name)

    # Build the Juju API endpoint based on the Juju version and environment id.
    api_url = jujutools.get_api_url(api_address, juju_version, env_uuid)

    # Retrieve the admin-secret for the current environment.
    print('retrieving the Juju environment credentials')
    username, password = app.get_credentials(options.env_name)

    print('connecting to {}'.format(api_url))
    env = app.connect(api_url, username, password)

    if already_bootstrapped:
        # Retrieve the environment type from the live environment: it may be
        # different from the one declared on the environments.yaml file.
        # Moreover, an imported jenv file could be in use, in which case the
        # environment type is probably still unknown.
        env_type = app.get_env_type(env)
    print('environment type: {}'.format(env_type))

    # Inspect the environment and deploy the charm if required.
    charm_ref, machine, service_data, unit_data = app.check_environment(
        env, settings.JUJU_GUI_SERVICE_NAME, options.charm_url,
        env_type, bootstrap_node_series, already_bootstrapped)
    unit_name = app.deploy_gui(
        env, settings.JUJU_GUI_SERVICE_NAME, charm_ref.id(), machine,
        service_data, unit_data)

    # Observe the deployment progress.
    address = app.watch(env, unit_name)
    env.close()

    # Print out Juju GUI unit and credential information.
    url = 'https://{}'.format(address)
    print('\nJuju GUI URL: {}\nusername: {}\npassword: {}\n'.format(
        url, username, password))

    # Connect to the GUI server WebSocket API.
    print('connecting to the Juju GUI server')
    gui_api_url = jujutools.get_api_url(
        address + ':443', juju_version, env_uuid,
        prefix='ws', charm_ref=charm_ref)
    gui_env = app.connect(gui_api_url, username, password)

    # Handle bundle deployment.
    if options.bundle_source is not None:
        services = ', '.join(options.bundle.services())
        print('requesting a deployment of {} with the following services:\n'
              '  {}'.format(options.bundle, services))
        if options.bundle.reference is not None:
            print('more details about this bundle can be found at\n'
                  '  {}'.format(options.bundle.reference.jujucharms_url()))
        # We need to connect to an API WebSocket server supporting bundle
        # deployments. The GUI builtin server, listening on the Juju GUI
        # address, exposes an API suitable for deploying bundles.
        app.deploy_bundle(gui_env, options.bundle)
        print('bundle deployment request accepted\n'
              'use the GUI to check the bundle deployment progress')

    if options.open_browser:
        token = app.create_auth_token(gui_env)
        if token is not None:
            url += '/?authtoken={}'.format(token)
        webbrowser.open(url)
    gui_env.close()
    print(
        'done!\n\n'
        'Run "juju quickstart -e {env_name}" again if you want\n'
        'to reopen and log in to the GUI browser later.\n'
        'Run "juju quickstart -i" if you want to manage\n'
        'or bootstrap your Juju environments using the\n'
        'interactive session.\n'
        'Run "juju destroy-environment {env_name} [-y]"\n'
        'to destroy the environment you just bootstrapped.'
        ''.format(env_name=options.env_name)
    )
