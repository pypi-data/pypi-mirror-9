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

"""Juju Quickstart environments management.

The objects included in this module help working with Juju environments.

The user environments are defined in the environments.yaml file stored inside
the JUJU_HOME (usually in ~/.juju/environments.yaml).

The load function is used to retrieve a memory representation of the
environments file. This representation is called "env_db" and it is just the
Python dictionary resulting from YAML decoding the environments file contents.
The env_db always includes an "environments" key and may or may not include
a "default" key, which specifies the default environment name.

After the environments representation is loaded in memory, it is possible to
retrieve the representation of a single environment using the get_env_data
function, e.g.:

    env_db = load('~/.juju/environments.yaml')
    env_data = get_env_data(env_db, 'myenv')

How the env_data is different from just env_db['environments']['myenv']?
The former stores two additional pieces of information: the environment name
(env_data['name']) and whether or not that environment is the default one
(env_data['is-default']). Retrieving an env_data also allows for easily
validating and normalizing the values in the environment, e.g.:

    errors = validate(env_metadata, env_data)
    new_env_data = normalize(env_metadata, env_data)

What is the "env_metadata" argument passed to the functions above? It is a
dictionary storing meta information about the provider type associated with
the env_data, and that can be applied to all the environments of that type.
For instance, env_metadata includes a list of expected fields and a description
suitable for that specific environment's type.

This meta information can be retrieved as follow:

    env_type_db = get_env_type_db()
    env_metadata = get_env_metadata(env_type_db, env_data)

Modifications to env_data can be easily applied to the original env_db using
the "set_env_data" function, and the resulting env_db can then be saved to
disk using the "save" function. In the following example an environment is
retrieved, validated, normalized and then saved back to disk:

    env_db = load('~/.juju/environments.yaml')
    env_type_db = get_env_type_db()
    env_data = get_env_data(env_db, 'myenv')
    env_metadata = get_env_metadata(env_type_db, env_data)
    errors = validate(env_metadata, env_data)
    if errors:
        # Handle errors...
    new_env_data = normalize(env_metadata, env_data)
    if new_env_data != env_data:  # The normalization process changed the data.
        set_env_data(env_db, 'myenv', new_env_data)
        save('~/.juju/environments.yaml', env_db)

The set_env_data function, as seen above, needs to be passed the original name
of the environment being modified. If None is passed, that means we are adding
a new environment.
"""

from __future__ import unicode_literals

import collections
import copy
import logging
import os
import re
import tempfile

from quickstart import (
    serializers,
    settings,
    utils,
)
from quickstart.models import fields


# Compile the regular expression used to parse the "juju switch" output.
_juju_switch_expression = re.compile(r'Current environment: "([\w-]+)"\n')


def get_default_env_name():
    """Return the current Juju environment name.

    The environment name can be set either by
        - setting the JUJU_ENV environment variable;
        - using "juju switch my-env-name";
        - setting the default environment in the environments.yaml file.
    The former overrides the latter.

    Return None if a default environment is not found.
    """
    env_name = os.getenv('JUJU_ENV', '').strip()
    if env_name:
        return env_name
    # The "juju switch" command parses ~/.juju/current-environment file. If the
    # environment name is not found there, then it tries to retrieve the name
    # from the "default" section of the ~/.juju/environments.yaml file.
    retcode, output, _ = utils.call('juju', 'switch')
    # Before juju-core 1.17, the "juju switch" command returns a human readable
    # output. Newer releases just output the environment name, or exit with an
    # error if no default environment is configured.
    if retcode:
        return None
    # Use a regular expression to check if "juju switch" returned a human
    # readable output.
    match = _juju_switch_expression.match(output)
    if match is not None:
        return match.groups()[0]
    # At this point we can safely assume we are using the newer "juju switch".
    return output.strip()


def create_empty_env_db():
    """Create and return an empty environments database."""
    return {'environments': {}}


def load(env_file):
    """Load and parse the provided Juju environments.yaml file.

    Return the decoded environments YAML as a dictionary, e.g.:

        {
            'default': 'myenv',
            'environments': {
                'myenv': {'type': 'ec2', ...},
                ...
            }
        }

    The resulting dictionary always has an "environments" keys, even if there
    are no environments defined in the Juju environments.yaml file.
    The "default" key instead is only set if the YAML includes a valid default
    environment.

    Raise a ValueError if:
        - the environment file is not found;
        - the environment file contents are not parsable by YAML;
        - the YAML contents are not properly structured.
    """
    contents = serializers.yaml_load_from_path(env_file)
    if contents is None:
        return create_empty_env_db()
    # Retrieve the environment list.
    try:
        env_contents = contents.get('environments', {}).items()
    except AttributeError:
        msg = 'invalid YAML contents in {}: {}'.format(env_file, contents)
        raise ValueError(msg.encode('utf-8'))
    environments = {}
    for env_name, env_info in env_contents:
        if isinstance(env_info, collections.Mapping):
            environments[env_name] = env_info
        else:
            logging.warn('excluding invalid environment {}'.format(env_name))
    # Build the resulting environments dict.
    env_db = {'environments': environments}
    default = contents.get('default')
    if default in environments:
        env_db['default'] = default
    elif default is not None:
        logging.warn('excluding invalid default {}'.format(default))
    return env_db


def save(env_file, env_db, backup_function=None):
    """Save the given env_db to the provided environments.yaml file.

    The new environments are saved to disk in the most atomic way possible.
    If backup_function is not None, it is called passing the original
    environments file path and the backup destination path. The backup is
    obviously performed only if the file exists.

    Raise an OSError if any errors occur in the process.
    """
    dirname = os.path.dirname(env_file)
    backup_file = None
    if os.path.exists(env_file):
        if backup_function is not None:
            # Create a backup of the original file.
            backup_file = env_file + '.quickstart.bak'
            backup_function(env_file, backup_file)
    else:
        utils.mkdir(dirname)
    banner = utils.get_quickstart_banner()
    # Save the contents in a temporary file, then rename to the real file.
    # Since the renaming operation may fail on some Unix flavors if the source
    # and destination files are on different file systems, use for the
    # temporary file the same directory where the env_file is stored.
    try:
        temp_file = tempfile.NamedTemporaryFile(
            prefix='quickstart-temp-envs-', dir=dirname, delete=False)
        temp_file.write(banner.encode('utf-8'))
        if backup_file is not None:
            temp_file.write(
                '# A backup copy of this file can be found in\n'
                '# {}\n\n'.format(backup_file))
        serializers.yaml_dump(env_db, temp_file)
    except Exception as err:
        raise OSError(err)
    # Ensure that all the data is written to disk.
    temp_file.flush()
    os.fsync(temp_file.fileno())
    temp_file.close()
    # Rename the temporary file to the real environments file.
    os.rename(temp_file.name, env_file)


def get_env_data(env_db, env_name):
    """Return the environment data for the given environment name.

    The env_data is a Python dictionary describing an environment as an entity
    separated from the env_db. For example, consider an env_db like this:

        {
            'default': 'myenv',
            'environments': {
                'myenv': {'type': 'local', 'admin-secret': 'Secret!'},
            },
        }

    The corresponding env_data for the "myenv" environment is the following:

        {
            # The name is now included in the data structure.
            'name': 'myenv',
            # The "is-default" field is always included.
            'is-default': True,
            # Remaining data is left as is.
            'type': 'local',
            'admin-secret': 'Secret!',
        }

    Raise a ValueError if the env_db does not include an environment with the
    given name.
    """
    try:
        info = env_db['environments'][env_name]
    except KeyError:
        msg = 'environment {} not found'.format(env_name)
        raise ValueError(msg.encode('utf-8'))
    # Why not just use env_data.copy()? Because this way internal mutable data
    # structures are preserved, even if they are unlikely to be found.
    env_data = copy.deepcopy(info)
    env_data.update({
        'is-default': env_db.get('default') == env_name,
        'name': env_name,
    })
    return env_data


def set_env_data(env_db, env_name, env_data):
    """Update the environments dictionary with the given environment data.

    The env_name argument is used as a reference to an existing environment
    in the env_db. If env_name is None, a new environment is added to the
    env_db. Otherwise the existing environment is updated using env_data.

    The env_data argument is an environment data dictionary, and must include
    at least the "name" and "is-default" keys.

    Raise a ValueError if:
        - env_data does not include a "name" key;
        - env_data does not include a "is-default" key;
        - env_data is a new environment and its name is already used by an
          existing environment;
        - env_data is an existing environment renamed, and its name is already
          used by another existing environment.

    If any errors occur, the env_db is left untouched.
    Without errors, the env_db is modified in place and None is returned.
    """
    new_env_data = copy.deepcopy(env_data)
    try:
        new_name = new_env_data.pop('name')
        is_default = new_env_data.pop('is-default')
    except KeyError:
        raise ValueError(b'invalid env_data: {!r}'.format(env_data))
    environments = env_db['environments']
    if (new_name != env_name) and (new_name in environments):
        raise ValueError(
            b'an environment named {!r} already exists'.format(new_name))
    if env_name is not None:
        del environments[env_name]
    environments[new_name] = new_env_data
    if is_default:
        env_db['default'] = new_name
    elif (env_db.get('default') == env_name) and (env_name is not None):
        del env_db['default']


def create_local_env_data(env_type_db, name, is_default=False):
    """Create and return a local (LXC) env_data.

    Local environments' fields (except for name and type) are assumed to be
    either optional or suitable for automatic generation of their values. For
    this reason local environments can be safely created given just their name.
    """
    env_data = {
        'type': 'local',
        'name': name,
        'is-default': is_default,
        # Workaround for bug 1306537: force tools for the most recent Juju GUI
        # supported series to be uploaded.
        'default-series': settings.JUJU_GUI_SUPPORTED_SERIES[-1],
    }
    env_metadata = get_env_metadata(env_type_db, env_data)
    # Retrieve a list of missing required fields.
    missing_fields = [
        field for field in env_metadata['fields']
        if field.required and field.name not in env_data]
    # The following fields are not generally required but should be
    # automatically generated for a local environment.
    forced_to_be_generated = ('admin-secret', )
    missing_fields.extend([field for field in env_metadata['fields']
                           if field.name in forced_to_be_generated])
    # Assume all missing fields can be automatically generated.
    env_data.update((field.name, field.generate()) for field in missing_fields)
    return env_data


def create_maas_env_data(env_type_db, name, server, api_key, is_default=False):
    """Create and return a MAAS (bare metal) env_data.

    The env_data is created using the given name, MAAS server and MAAS OAuth
    API key.
    """
    env_data = {
        'type': 'maas',
        'name': name,
        'is-default': is_default,
        'maas-server': server,
        'maas-oauth': api_key,
    }
    env_metadata = get_env_metadata(env_type_db, env_data)
    # Retrieve a list of missing required fields.
    missing_fields = [
        field for field in env_metadata['fields']
        if field.required and field.name not in env_data]
    # Assume all missing fields can be automatically generated.
    env_data.update((field.name, field.generate()) for field in missing_fields)
    return env_data


def remove_env(env_db, env_name):
    """Remove the environment named env_name from the environments database.

    Raise a ValueError if the environment is not present in env_db.
    Without errors, the env_db is modified in place and None is returned.
    """
    environments = env_db['environments']
    try:
        del environments[env_name]
    except KeyError:
        raise ValueError(
            b'the environment named {!r} does not exist'.format(env_name))
    if env_db.get('default') == env_name:
        del env_db['default']
    # If only one environment remains, set it as default.
    if len(environments) == 1:
        env_db['default'] = environments.keys()[0]


def get_env_type_db():
    """Return the environments meta information based on provider types.

    The env_type_db describes Juju environments based on their provider type.

    The returned data is a dictionary mapping provider type names to meta
    information. A provider named "__fallback__" is also included and can be
    used to minimally handle environments whose type is not currently supported
    by quickstart.
    """
    # Define a collection of fields shared by many environment types.
    provider_field = fields.StringField(
        'type', label='provider type', required=True, readonly=True,
        help='the provider type enabled for this environment')
    name_field = fields.StringField(
        'name', label='environment name', required=True,
        help='the environment name to use with Juju (arbitrary string)')
    admin_secret_field = fields.AutoGeneratedPasswordField(
        'admin-secret', label='admin secret', required=False,
        help='the password used to authenticate to the environment')
    default_series_field = fields.ChoiceField(
        'default-series', choices=settings.JUJU_DEFAULT_SERIES,
        label='default series', required=False,
        help='the default Ubuntu series to use for the bootstrap node')
    is_default_field = fields.BoolField(
        'is-default', label='default', allow_mixed=False, required=True,
        help='make this the default environment')
    # Define data structures used as part of the metadata below.
    ec2_regions = (
        'ap-northeast-1', 'ap-southeast-1', 'ap-southeast-2',
        'eu-west-1', 'sa-east-1',
        'us-east-1', 'us-west-1', 'us-west-2',
    )
    hp_regions = ('region-a.geo-1', 'region-b.geo-1')
    azure_locations = (
        'East US', 'West US', 'West Europe', 'North Europe',
        'Southeast Asia', 'East Asia')
    # The first URL is used as the default one.
    joyent_sdc_urls = (
        'https://us-west-1.api.joyentcloud.com',
        'https://us-east-1.api.joyentcloud.com',
        'https://us-sw-1.api.joyentcloud.com',
        'https://us-ams-1.api.joyentcloud.com',
    )
    # Define the env_type_db dictionary: this is done inside this function in
    # order to avoid instantiating fields at import time.
    # This is an ordered dict so that views can expose options to create new
    # environments in the order we like.
    env_type_db = collections.OrderedDict({
        '__fallback__': {
            'description': (
                'This provider type is not supported by quickstart. '
                'See https://juju.ubuntu.com/docs/getting-started.html for '
                'a description of how to get started with Juju.'
            ),
            'fields': (
                provider_field,
                name_field,
                admin_secret_field,
                default_series_field,
                is_default_field,
            ),
        },
    })
    env_type_db['ec2'] = {
        'label': 'Amazon EC2',
        'description': (
            'The ec2 provider enables you to run Juju on the EC2 cloud. '
            'This process requires you to have an Amazon Web Services (AWS) '
            'account. If you have not signed up for one yet, it can obtained '
            'at http://aws.amazon.com. '
            'See https://juju.ubuntu.com/docs/config-aws.html for more '
            'details on the ec2 provider configuration.'
        ),
        'fields': (
            provider_field,
            # Required fields.
            name_field,
            fields.PasswordField(
                'access-key', label='access key', required=True,
                help='The access key to use to authenticate to AWS. '
                     'You can retrieve these values easily from your AWS '
                     'Management Console (http://console.aws.amazon.com). '
                     'Click on your name in the top-right and then the '
                     '"Security Credentials" link from the drop down menu. '
                     'Under the "Access Keys" heading click the '
                     '"Create New Root Key" button. You will be prompted to '
                     '"Download Key File" which by default is named '
                     'rootkey.csv. Open this file to get the access-key and '
                     'secret-key for the environments.yaml config file.'),
            fields.PasswordField(
                'secret-key', label='secret key', required=True,
                help='The secret key to use to authenticate to AWS. '
                     'See the access key help above.'),
            # Optional fields.
            fields.ChoiceField(
                'region', choices=ec2_regions, default='us-east-1',
                label='region', required=False, help='the ec2 region to use'),
            admin_secret_field,
            default_series_field,
            fields.AutoGeneratedStringField(
                'control-bucket', label='control bucket', required=False,
                help='the globally unique S3 bucket name'),
            is_default_field,
        ),
    }
    env_type_db['openstack'] = {
        'label': 'OpenStack (or HP Public Cloud)',
        'description': (
            'The openstack provider enables you to run Juju on OpenStack '
            'private and public clouds. Use this also if you want to '
            'set up Juju on HP Public Cloud. See '
            'https://juju.ubuntu.com/docs/config-openstack.html and '
            'https://juju.ubuntu.com/docs/config-hpcloud.html for more '
            'details on the openstack provider configuration.'
        ),
        'fields': (
            provider_field,
            # Required fields.
            name_field,
            fields.SuggestionsStringField(
                'auth-url', label='authentication URL', required=True,
                help='The Keystone URL to use in the authentication process. '
                     'For HP Public Cloud, use the value suggested below:',
                suggestions=['https://region-a.geo-1.identity.hpcloudsvc.com'
                             ':35357/v2.0/']),
            fields.StringField(
                'tenant-name', label='tenant name', required=True,
                help='The OpenStack tenant name. For HP Public Cloud, this is '
                     'listed as the project name on the '
                     'https://horizon.hpcloud.com/landing/ page.'),
            fields.BoolField(
                'use-floating-ip', label='use floating IP', allow_mixed=False,
                required=True,
                help='Specifies whether the use of a floating IP address is '
                     'required to give the nodes a public IP address. '
                     'Some installations assign public IP addresses by '
                     'default without requiring a floating IP address. '
                     'For HP Public Cloud, floating IP must be activated.'),
            fields.SuggestionsStringField(
                'region', label='region', required=True,
                help='The OpenStack region to use. '
                     'For HP Public Cloud, use one of the following:',
                suggestions=hp_regions),
            # Optional fields.
            fields.ChoiceField(
                'auth-mode', label='authentication mode', required=False,
                default='userpass', choices=('userpass', 'keypair'),
                help='The way Juju authenticates to OpenStack. The userpass '
                     'authentication requires you to fill in your user name '
                     'and password. The keypair mode requires access key and '
                     'secret key to be properly set up. For HP Public Cloud, '
                     'select userpass mode and type your HP Cloud login '
                     'user name and password below.'),
            fields.StringField(
                'username', label='user name', required=False,
                help='the user name to use for the userpass authentication '
                     '(or the HP Cloud login user name)'),
            fields.PasswordField(
                'password', label='password', required=False,
                help='the user name to use for the userpass authentication '
                     '(or the HP Cloud login password)'),
            fields.StringField(
                'access-key', label='access key', required=False,
                help='the access key to use for the keypair authentication'),
            fields.PasswordField(
                'secret-key', label='secret key', required=False,
                help='the secret key to use for the keypair authentication'),
            fields.AutoGeneratedStringField(
                'control-bucket', label='control bucket', required=False,
                help='the globally unique swift bucket name'),
            admin_secret_field,
            default_series_field,
            is_default_field,
        ),
    }
    env_type_db['azure'] = {
        'label': 'Windows Azure',
        'description': (
            'The azure provider enables you to run Juju on Windows Azure. '
            'It requires you to have an Windows Azure account. If you have '
            'not signed up for one yet, it can obtained at '
            'http://www.windowsazure.com/. See '
            'https://juju.ubuntu.com/docs/config-azure.html for more '
            'details on the azure provider configuration.'
        ),
        'fields': (
            provider_field,
            # Required fields.
            name_field,
            fields.StringField(
                'management-subscription-id', required=True,
                label='management subscription ID',
                help='this information can be retrieved from '
                     'https://manage.windowsazure.com (Settings)'),
            fields.FilePathField(
                'management-certificate-path', required=True,
                label='management certificate path',
                help='the path to the pem file associated to the certificate '
                     'uploaded in the Azure management console: '
                     'https://manage.windowsazure.com '
                     '(Settings -> Management Certificates)'),
            fields.StringField(
                'storage-account-name', required=True,
                label='storage account name',
                help='the name you used when creating a storage account in '
                     'the Azure management console: '
                     'https://manage.windowsazure.com (Storage). '
                     'You must create the storage account in the same '
                     'region/location specified by the location key value.'),
            fields.ChoiceField(
                'location', choices=azure_locations, label='location',
                required=True, help='the region to use'),
            # Optional fields.
            admin_secret_field,
            default_series_field,
            is_default_field,
        ),
    }
    env_type_db['joyent'] = {
        'label': 'Joyent',
        'description': (
            'The joyent provider enables you to run Juju on the Joyent cloud. '
            'This process requires you to have a Joyent account. If you have '
            'not signed up for one yet, it can obtained at '
            'http://www.joyent.com/. See '
            'https://juju.ubuntu.com/docs/config-joyent.html for more details '
            'on the joyent provider configuration.'
        ),
        'fields': (
            provider_field,
            name_field,
            # SDC fields.
            fields.StringField(
                'sdc-user', required=True,
                label='SDC user name',
                help='The Smart Data Center account name. '
                     'This is usually your Joyent user name.'),
            fields.StringField(
                'sdc-key-id', required=True,
                label='SDC key id',
                help='the SSH public key fingerprint used to connect to the '
                     'Smart Data Center'),
            fields.ChoiceField(
                'sdc-url', choices=joyent_sdc_urls, label='SDC URL',
                required=False, default=joyent_sdc_urls[0],
                help='the region URL to use for SDC'),
            # Manta fields.
            fields.StringField(
                'manta-user', required=True,
                label='manta user name',
                help='The Manta Storage Service account name. '
                     'This is usually your Joyent user name.'),
            fields.StringField(
                'manta-key-id', required=True,
                label='manta key id',
                help='The SSH public key fingerprint used to connect to the '
                     'Manta Storage Service. This is usually the same SSH '
                     'fingerprint provided as SDC key id.'),
            fields.StringField(
                'manta-url', label='manta URL', required=False,
                default='https://us-east.manta.joyent.com',
                help='the region URL to use for manta'),
            # Optional fields.
            fields.FilePathField(
                'private-key-path', label='private key path', required=False,
                default='~/.ssh/id_rsa',
                help='the path to the SSH private key'),
            fields.StringField(
                'algorithm', label='SSH algorithm', required=False,
                default='rsa-sha256'),
            admin_secret_field,
            default_series_field,
            is_default_field,
        ),
    }
    env_type_db['maas'] = {
        'label': 'MAAS (bare metal)',
        'description': (
            'Metal As A Service is software which allows you to deal with '
            'physical hardware just as easily as virtual nodes. MAAS lets you '
            'treat physical servers like virtual machines in the cloud. '
            'Rather than having to manage each server individually, MAAS '
            'turns your bare metal into an elastic cloud-like resource. '
            'Specifically, MAAS allows for services to be deployed to bare '
            'metal via Juju. '
            'See https://juju.ubuntu.com/docs/config-maas.html and '
            'http://maas.ubuntu.com/ for more information about MAAS.'
        ),
        'fields': (
            provider_field,
            # Required fields.
            name_field,
            fields.StringField(
                'maas-server', label='server address', required=True,
                help='The MAAS server address, for instance '
                     'http://<my-maas-server>/MAAS.'),
            fields.PasswordField(
                'maas-oauth', label='API key', required=True,
                help='The MAAS API key. This can be found by going to the '
                     'MAAS user preferences page (/MAAS/account/prefs/). A '
                     'link to the account preferences is accessible from the '
                     'drop-down menu that appears when clicking your user '
                     'name at the top-right of the page.'),
            # Optional fields.
            fields.FilePathField(
                'authorized-keys-path', required=False,
                label='SSH public key file',
                help='If keys are specified, MAAS will be able to '
                     'automatically add them to each unit it manages.'),
            admin_secret_field,
            default_series_field,
            is_default_field,
        ),
    }
    env_type_db['manual'] = {
        'label': 'Manual Provisioning',
        'description': (
            'Juju provides a feature called "Manual Provisioning" that '
            'enables you to deploy Juju, and charms, to existing systems. '
            'This is useful if you have groups of machines that you want to '
            "use for Juju but don't want to add the complexity of a new "
            'OpenStack or MAAS setup. It is also useful as a means of '
            'deploying workloads to VPS providers and other cheap hosting '
            'options. Manual provisioning enables you to run Juju on systems '
            'that have a supported operating system installed. You will need '
            'to ensure that you have both SSH access and sudo rights. '
            'See https://juju.ubuntu.com/docs/config-manual.html for more '
            'details on the manual provider configuration, including its '
            'caveats and limitattions.'
        ),
        'fields': (
            provider_field,
            # Required fields.
            name_field,
            fields.StringField(
                'bootstrap-host', label='bootstrap host', required=True,
                help='The host name/IP address of the machine where the '
                     'bootstrap machine agent will be started.'),
            # Optional fields.
            fields.StringField(
                'bootstrap-user', label='bootstrap user', required=False,
                help='The user name to authenticate as when connecting to the '
                     'bootstrap machine. It defaults to the current user.'),
            fields.StringField(
                'storage-listen-ip', label='storage listen IP', required=False,
                help="The IP address that the bootstrap machine's Juju "
                     'storage server will listen on. By default, storage will '
                     'be served on all network interfaces.'),
            fields.IntField(
                'storage-port', min_value=1, max_value=65535,
                label='storage port', required=False, default=8040,
                help="The TCP port that the bootstrap machine's Juju storage "
                     'server will listen on.'),
            admin_secret_field,
            is_default_field,
        ),
    }
    env_type_db['local'] = {
        'label': 'local (LXC)',
        'description': (
            'The LXC local provider enables you to run Juju on a single '
            'system like your local computer or a single server. '
            'See https://juju.ubuntu.com/docs/config-LXC.html for more '
            'details on the local provider configuration.'
        ),
        'fields': (
            provider_field,
            name_field,
            # LXC related fields.
            fields.BoolField(
                'lxc-clone', label='use lxc-clone', required=False,
                help='Use lxc-clone to create the containers used as '
                     'machines. LXC clone is enabled by default for Trusty '
                     'and above, and disabled for earlier Ubuntu releases.'),
            fields.BoolField(
                'lxc-clone-aufs', label='use lxc-clone-aufs', required=False,
                help='Use aufs as a backing-store for the LXC clones. Note '
                     "that there are some situations where aufs doesn't "
                     'entirely behave as intuitively as one might expect. '
                     'If not specified, aufs is not used.'),
            fields.StringField(
                'root-dir', label='root dir', required=False,
                default='~/.juju/local',
                help='the directory that is used for the storage files'),
            fields.IntField(
                'storage-port', min_value=1, max_value=65535,
                label='storage port', required=False, default=8040,
                help='override if you have multiple local providers, '
                     'or if the default port is used by another program'),
            fields.IntField(
                'shared-storage-port', min_value=1, max_value=65535,
                label='shared storage port', required=False, default=8041,
                help='override if you have multiple local providers, '
                     'or if the default port is used by another program'),
            fields.StringField(
                'network-bridge', label='network bridge', required=False,
                default='lxcbr0', help='the LXC bridge interface to use'),
            # Other optional fields.
            admin_secret_field,
            default_series_field,
            is_default_field,
        ),
    }
    return env_type_db


def get_supported_env_types(env_type_db, filter_function=None):
    """Return a list of supported (provider type, label) tuples.

    Each tuple represents an environment type supported by Quickstart.
    It is possible to filter results by providing a filter_function callable
    which receives the environment type and metadata.
    """
    if filter_function is None:
        filter_function = lambda env_type, metadata: True
    return [
        (env_type, metadata['label'])
        for env_type, metadata in env_type_db.items()
        if (env_type != '__fallback__') and filter_function(env_type, metadata)
    ]


def get_env_metadata(env_type_db, env_data):
    """Return the meta information (fields, description) suitable for env_data.

    Use the given env_type_db to retrieve the metadata corresponding to the
    environment type included in env_data.

    The resulting metadata can be used to parse/validate environments or to
    enrich the user experience e.g. by providing additional information about
    the fields composing a specific environment type, or about the environment
    type itself.
    """
    env_type = env_data.get('type', '__fallback__')
    return env_type_db.get(env_type, env_type_db['__fallback__'])


def map_fields_to_env_data(env_metadata, env_data):
    """Return a list of (field, value) tuples.

    Each tuple stores a field (instance of fields.Field or its subclasses)
    describing a specific environment key in env_data, and the corresponding
    value in env_data.

    If extraneous keys (not described by env_metadata) are found in env_data,
    then those keys are assigned a generic default field (fields.Field).
    """
    data = copy.deepcopy(env_data)
    # Start building a list of (field, value) pairs preserving field order.
    field_value_pairs = [
        (field, data.pop(field.name, None))
        for field in env_metadata['fields']
    ]
    # Add the remaining (unexpected) pairs using the unexpected field type.
    field_value_pairs.extend(
        (fields.UnexpectedField(key), value)
        for key, value in data.items()
    )
    return field_value_pairs


def validate(env_metadata, env_data):
    """Validate values in env_data.

    Return a dictionary of errors mapping field names to error messages.
    If the environment is valid, return an empty dictionary.
    """
    errors = {}
    for field, value in map_fields_to_env_data(env_metadata, env_data):
        try:
            field.validate(value)
        except ValueError as err:
            errors[field.name] = bytes(err).decode('utf-8')
    return errors


def normalize(env_metadata, env_data):
    """Normalize the values in env_data.

    Return a new env_data containing the normalized values.
    This function assumes env_data contains valid values.
    """
    normalized_env_data = {}
    for field, value in map_fields_to_env_data(env_metadata, env_data):
        value = field.normalize(value)
        # Only include the key/value pair if the corresponding field is
        # required or the value is set.
        if field.required or value is not None:
            normalized_env_data[field.name] = value
    return normalized_env_data


def get_env_short_description(env_data):
    """Return a short description of the given env_data.

    The given env_data must include at least the "name" and "is-default" keys.

    The description is like the following:
        "aws (type: ec2, default)"  # Default ec2 environment.
        "lxc (type: local)"  # Non-default local environment.
        "unknown"  # An environment with no type set.
    """
    info_parts = []
    env_type = env_data.get('type')
    if env_type is not None:
        info_parts.append('type: {}'.format(env_type))
    if env_data['is-default']:
        info_parts.append('default')
    info = ''
    if info_parts:
        info = ' ({})'.format(', '.join(info_parts))
    return env_data['name'] + info
