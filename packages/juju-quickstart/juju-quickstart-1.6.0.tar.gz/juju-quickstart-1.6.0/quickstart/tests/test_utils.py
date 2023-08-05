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

"""Tests for the Juju Quickstart utility functions and classes."""

from __future__ import unicode_literals

import datetime
import json
import os
import shutil
import tempfile
import unittest

import mock
import yaml

from quickstart import (
    get_version,
    settings,
    utils,
)
from quickstart.models import charms
from quickstart.tests import helpers


@helpers.mock_print
class TestAddAptRepository(helpers.CallTestsMixin, unittest.TestCase):

    apt_add_repository = '/usr/bin/add-apt-repository'
    apt_get = '/usr/bin/apt-get'
    repository = 'ppa:good/stuff'
    side_effects = (
        (0, 'apt-get install', ''),  # Install add-apt-repository.
        (0, 'add-apt-repository', ''),  # Add the repository.
        (0, 'update', ''),  # Update the global repository
    )

    def patch_codename(self, codename):
        """Patch the Ubuntu codename returned by get_ubuntu_codename."""
        return mock.patch(
            'quickstart.utils.get_ubuntu_codename',
            mock.Mock(return_value=codename))

    def test_precise(self, mock_print):
        # The repository is properly added in precise.
        with self.patch_codename('precise') as mock_get_ubuntu_codename:
            with self.patch_multiple_calls(self.side_effects) as mock_call:
                utils.add_apt_repository(self.repository)
        mock_get_ubuntu_codename.assert_called_once_with()
        self.assertEqual(len(self.side_effects), mock_call.call_count)
        mock_call.assert_has_calls([
            mock.call('sudo', self.apt_get, 'install', '-y',
                      'python-software-properties'),
            mock.call('sudo', self.apt_add_repository, '-y', self.repository),
            mock.call('sudo', self.apt_get, 'update'),
        ])

    def test_after_precise(self, mock_print):
        # The repository is correctly added in newer releases.
        with self.patch_codename('trusty') as mock_get_ubuntu_codename:
            with self.patch_multiple_calls(self.side_effects) as mock_call:
                utils.add_apt_repository(self.repository)
        mock_get_ubuntu_codename.assert_called_once_with()
        self.assertEqual(len(self.side_effects), mock_call.call_count)
        mock_call.assert_has_calls([
            mock.call('sudo', self.apt_get, 'install', '-y',
                      'software-properties-common'),
            mock.call('sudo', self.apt_add_repository, '-y', self.repository),
            mock.call('sudo', self.apt_get, 'update'),
        ])

    def test_output(self, mock_print):
        # The user is properly informed about the process.
        with self.patch_codename('raring'):
            with self.patch_multiple_calls(self.side_effects):
                utils.add_apt_repository(self.repository)
        self.assertEqual(2, mock_print.call_count)
        mock_print.assert_has_calls([
            mock.call('adding the {} PPA repository'.format(self.repository)),
            mock.call('sudo privileges will be required for PPA installation'),
        ])

    def test_command_error(self, mock_print):
        # An OSError is raised if a command error occurs.
        side_effects = [(1, '', 'apt-get install error')]
        with self.patch_codename('quantal') as mock_get_ubuntu_codename:
            with self.patch_multiple_calls(side_effects) as mock_call:
                with self.assertRaises(OSError) as context_manager:
                    utils.add_apt_repository(self.repository)
        mock_get_ubuntu_codename.assert_called_once_with()
        mock_call.assert_called_once_with(
            'sudo', self.apt_get, 'install', '-y',
            'software-properties-common')
        self.assertEqual(
            'apt-get install error', bytes(context_manager.exception))


class TestCall(unittest.TestCase):

    def test_success(self):
        # A zero exit code and the subprocess output are correctly returned.
        retcode, output, error = utils.call('echo')
        self.assertEqual(0, retcode)
        self.assertEqual('\n', output)
        self.assertEqual('', error)

    def test_multiple_arguments(self):
        # A zero exit code and the subprocess output are correctly returned
        # when executing a command passing multiple arguments.
        retcode, output, error = utils.call('echo', 'we are the borg!')
        self.assertEqual(0, retcode)
        self.assertEqual('we are the borg!\n', output)
        self.assertEqual('', error)

    def test_failure(self):
        # An error code and the error are returned if the subprocess fails.
        retcode, output, error = utils.call('ls', 'no-such-file')
        self.assertNotEqual(0, retcode)
        self.assertEqual('', output)
        self.assertIn('No such file or directory', error)

    def test_invalid_command(self):
        # An error code and the error are returned if the subprocess fails to
        # find the provided command in the PATH.
        retcode, output, error = utils.call('no-such-command')
        self.assertEqual(127, retcode)
        self.assertEqual('', output)
        self.assertEqual(
            'no-such-command: [Errno 2] No such file or directory',
            error)

    def test_logging(self):
        # The command line call and the results are properly logged.
        expected_messages = (
            "running the following: echo 'we are the borg!'",
            r"retcode: 0 | output: 'we are the borg!\n' | error: ''",
        )
        with helpers.assert_logs(expected_messages):
            utils.call('echo', 'we are the borg!')


@mock.patch('__builtin__.print', mock.Mock())
class TestParseGuiCharmUrl(unittest.TestCase):

    def test_charm_instance_returned(self):
        # A charm instance is correctly returned.
        charm = utils.parse_gui_charm_url('cs:trusty/juju-gui-42')
        self.assertIsInstance(charm, charms.Charm)
        self.assertEqual('cs:trusty/juju-gui-42', charm.url())

    def test_customized(self):
        # A customized charm URL is properly logged.
        expected = 'using a customized juju-gui charm'
        with helpers.assert_logs([expected], level='warn'):
            utils.parse_gui_charm_url('cs:~juju-gui/precise/juju-gui-28')

    def test_outdated(self):
        # An outdated charm URL is properly logged.
        expected = 'charm is outdated and may not support bundle deployments'
        with helpers.assert_logs([expected], level='warn'):
            utils.parse_gui_charm_url('cs:precise/juju-gui-1')

    def test_unexpected(self):
        # An unexpected charm URL is properly logged.
        expected = (
            'unexpected URL for the juju-gui charm: the service may not work '
            'as expected')
        with helpers.assert_logs([expected], level='warn'):
            utils.parse_gui_charm_url('cs:precise/another-gui-42')

    def test_official(self):
        # No warnings are logged if an up to date charm is passed.
        with mock.patch('logging.warn') as mock_warn:
            utils.parse_gui_charm_url('cs:precise/juju-gui-100')
        self.assertFalse(mock_warn.called)


class TestConvertBundleUrl(helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_full_bundle_url(self):
        # The HTTPS location to the YAML contents is correctly returned.
        bundle_url = 'bundle:~myuser/wiki-bundle/42/wiki'
        url, bundle_id = utils.convert_bundle_url(bundle_url)
        self.assertEqual(
            'https://manage.jujucharms.com'
            '/bundle/~myuser/wiki-bundle/42/wiki/json', url)
        self.assertEqual('~myuser/wiki-bundle/42/wiki', bundle_id)

    def test_bundle_url_right_strip(self):
        # The trailing slash in the bundle URL is removed.
        bundle_url = 'bundle:~myuser/wiki-bundle/42/wiki/'
        url, bundle_id = utils.convert_bundle_url(bundle_url)
        self.assertEqual(
            'https://manage.jujucharms.com'
            '/bundle/~myuser/wiki-bundle/42/wiki/json', url)
        self.assertEqual('~myuser/wiki-bundle/42/wiki', bundle_id)

    def test_bundle_url_no_revision(self):
        # The bundle revision is optional.
        bundle_url = 'bundle:~myuser/wiki-bundle/wiki-simple'
        url, bundle_id = utils.convert_bundle_url(bundle_url)
        self.assertEqual(
            'https://manage.jujucharms.com'
            '/bundle/~myuser/wiki-bundle/wiki-simple/json', url)
        self.assertEqual('~myuser/wiki-bundle/wiki-simple', bundle_id)

    def test_bundle_url_no_user(self):
        # If the bundle user is not specified, the bundle is assumed to be
        # promulgated and owned by "charmers".
        bundle_url = 'bundle:wiki-bundle/1/wiki'
        url, bundle_id = utils.convert_bundle_url(bundle_url)
        self.assertEqual(
            'https://manage.jujucharms.com'
            '/bundle/~charmers/wiki-bundle/1/wiki/json', url)
        self.assertEqual('~charmers/wiki-bundle/1/wiki', bundle_id)

    def test_bundle_url_short_form(self):
        # A promulgated bundle URL can just include the basket and the name.
        bundle_url = 'bundle:wiki-bundle/wiki'
        url, bundle_id = utils.convert_bundle_url(bundle_url)
        self.assertEqual(
            'https://manage.jujucharms.com'
            '/bundle/~charmers/wiki-bundle/wiki/json', url)
        self.assertEqual('~charmers/wiki-bundle/wiki', bundle_id)

    def test_full_jujucharms_url(self):
        # The HTTPS location to the YAML contents is correctly returned.
        url, bundle_id = utils.convert_bundle_url(
            settings.JUJUCHARMS_BUNDLE_URL + '~myuser/wiki-bundle/42/wiki')
        self.assertEqual(
            'https://manage.jujucharms.com'
            '/bundle/~myuser/wiki-bundle/42/wiki/json', url)
        self.assertEqual('~myuser/wiki-bundle/42/wiki', bundle_id)

    def test_jujucharms_url_right_strip(self):
        # The trailing slash in the jujucharms URL is removed.
        url, bundle_id = utils.convert_bundle_url(
            settings.JUJUCHARMS_BUNDLE_URL + '~charmers/mediawiki/6/scalable/')
        self.assertEqual(
            'https://manage.jujucharms.com'
            '/bundle/~charmers/mediawiki/6/scalable/json', url)
        self.assertEqual('~charmers/mediawiki/6/scalable', bundle_id)

    def test_jujucharms_url_no_revision(self):
        # The bundle revision is optional.
        url, bundle_id = utils.convert_bundle_url(
            settings.JUJUCHARMS_BUNDLE_URL + '~myuser/wiki/wiki-simple/')
        self.assertEqual(
            'https://manage.jujucharms.com'
            '/bundle/~myuser/wiki/wiki-simple/json', url)
        self.assertEqual('~myuser/wiki/wiki-simple', bundle_id)

    def test_jujucharms_url_no_user(self):
        # If the bundle user is not specified, the bundle is assumed to be
        # promulgated and owned by "charmers".
        url, bundle_id = utils.convert_bundle_url(
            settings.JUJUCHARMS_BUNDLE_URL + 'mediawiki/42/single/')
        self.assertEqual(
            'https://manage.jujucharms.com'
            '/bundle/~charmers/mediawiki/42/single/json', url)
        self.assertEqual('~charmers/mediawiki/42/single', bundle_id)

    def test_jujucharms_url_short_form(self):
        # A jujucharms URL for a promulgated bundle can just include the basket
        # and the name.
        url, bundle_id = utils.convert_bundle_url(
            settings.JUJUCHARMS_BUNDLE_URL + 'wiki-bundle/wiki/')
        self.assertEqual(
            'https://manage.jujucharms.com'
            '/bundle/~charmers/wiki-bundle/wiki/json', url)
        self.assertEqual('~charmers/wiki-bundle/wiki', bundle_id)

    def test_error(self):
        # A ValueError is raised if the bundle/jujucharms URL is not valid.
        bad_urls = (
            'bad', 'bundle:', 'bundle:~user', 'bundle:no-such',
            'bundle:~user/name', 'bundle:~user/basket/revision/name',
            'bundle:basket/name//', 'bundle:basket.name/bundle.name',
            settings.JUJUCHARMS_BUNDLE_URL,
            settings.JUJUCHARMS_BUNDLE_URL + 'bad',
            settings.JUJUCHARMS_BUNDLE_URL + '~user/no-such',
            settings.JUJUCHARMS_BUNDLE_URL + '~user/basket/revision/name/',
            settings.JUJUCHARMS_BUNDLE_URL + '~user/basket/42/name/error',
            'https://jujucharms.com/charms/mediawiki/simple/',
        )
        for url in bad_urls:
            with self.assert_value_error('invalid bundle URL: {}'.format(url)):
                utils.convert_bundle_url(url)


class TestGetQuickstartBanner(unittest.TestCase):

    def patch_datetime(self):
        mock_datetime = mock.Mock()
        mock_datetime.utcnow.return_value = datetime.datetime(
            2014, 2, 27, 7, 42, 47)
        return mock.patch('datetime.datetime', mock_datetime)

    def test_banner(self):
        # The banner is correctly generated.
        with self.patch_datetime():
            obtained = utils.get_quickstart_banner()
        expected = (
            '# This file has been generated by juju quickstart v{}\n'
            '# at 2014-02-27 07:42:47 UTC.\n\n'
        ).format(get_version())
        self.assertEqual(expected, obtained)


class TestGetServiceInfo(helpers.WatcherDataTestsMixin, unittest.TestCase):

    def test_service_and_unit(self):
        # The data about the given service and unit is correctly returned.
        service_change = self.make_service_change()
        unit_change = self.make_unit_change()
        status = [service_change, unit_change]
        expected = (service_change[2], unit_change[2])
        self.assertEqual(expected, utils.get_service_info(status, 'my-gui'))

    def test_service_only(self):
        # The data about the given service without units is correctly returned.
        service_change = self.make_service_change()
        status = [service_change]
        expected = (service_change[2], None)
        self.assertEqual(expected, utils.get_service_info(status, 'my-gui'))

    def test_service_removed(self):
        # A tuple (None, None) is returned if the service is being removed.
        status = [
            self.make_service_change(action='remove'),
            self.make_unit_change(),
        ]
        expected = (None, None)
        self.assertEqual(expected, utils.get_service_info(status, 'my-gui'))

    def test_another_service(self):
        # A tuple (None, None) is returned if the service is not found.
        status = [
            self.make_service_change(data={'Name': 'another-service'}),
            self.make_unit_change(),
        ]
        expected = (None, None)
        self.assertEqual(expected, utils.get_service_info(status, 'my-gui'))

    def test_service_not_alive(self):
        # A tuple (None, None) is returned if the service is not alive.
        status = [
            self.make_service_change(data={'Life': 'dying'}),
            self.make_unit_change(),
        ]
        expected = (None, None)
        self.assertEqual(expected, utils.get_service_info(status, 'my-gui'))

    def test_unit_removed(self):
        # The unit data is not returned if the unit is being removed.
        service_change = self.make_service_change()
        status = [service_change, self.make_unit_change(action='remove')]
        expected = (service_change[2], None)
        self.assertEqual(expected, utils.get_service_info(status, 'my-gui'))

    def test_another_unit(self):
        # The unit data is not returned if the unit belongs to another service.
        service_change = self.make_service_change()
        status = [
            service_change,
            self.make_unit_change(data={'Service': 'another-service'}),
        ]
        expected = (service_change[2], None)
        self.assertEqual(expected, utils.get_service_info(status, 'my-gui'))

    def test_no_services(self):
        # A tuple (None, None) is returned no services are found.
        status = [self.make_unit_change()]
        expected = (None, None)
        self.assertEqual(expected, utils.get_service_info(status, 'my-gui'))

    def test_no_entities(self):
        # A tuple (None, None) is returned no entities are found.
        expected = (None, None)
        self.assertEqual(expected, utils.get_service_info([], 'my-gui'))


class TestGetUbuntuCodename(helpers.CallTestsMixin, unittest.TestCase):

    def test_codename(self):
        # The distribution codename is correctly returned.
        with self.patch_call(0, output='trusty\n') as mock_call:
            codename = utils.get_ubuntu_codename()
        self.assertEqual('trusty', codename)
        mock_call.assert_called_once_with('lsb_release', '-cs')

    def test_error_retrieving_codename(self):
        # An OSError is returned if the codename cannot be retrieved.
        with self.patch_call(1, error='bad wolf') as mock_call:
            with self.assertRaises(OSError) as context_manager:
                utils.get_ubuntu_codename()
        self.assertEqual('bad wolf', bytes(context_manager.exception))
        mock_call.assert_called_once_with('lsb_release', '-cs')


class TestMkdir(unittest.TestCase):

    def setUp(self):
        # Set up a playground directory.
        self.playground = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.playground)

    def test_create_dir(self):
        # A directory is correctly created.
        path = os.path.join(self.playground, 'foo')
        utils.mkdir(path)
        self.assertTrue(os.path.isdir(path))

    def test_intermediate_dirs(self):
        # All intermediate directories are created.
        path = os.path.join(self.playground, 'foo', 'bar', 'leaf')
        utils.mkdir(path)
        self.assertTrue(os.path.isdir(path))

    def test_expand_user(self):
        # The ~ construction is expanded.
        with mock.patch('os.environ', {'HOME': self.playground}):
            utils.mkdir('~/in/my/home')
        path = os.path.join(self.playground, 'in', 'my', 'home')
        self.assertTrue(os.path.isdir(path))

    def test_existing_dir(self):
        # The function exits without errors if the target directory exists.
        path = os.path.join(self.playground, 'foo')
        os.mkdir(path)
        utils.mkdir(path)

    def test_existing_file(self):
        # An OSError is raised if a file already exists in the target path.
        path = os.path.join(self.playground, 'foo')
        with open(path, 'w'):
            with self.assertRaises(OSError):
                utils.mkdir(path)

    def test_failure(self):
        # Errors are correctly re-raised.
        path = os.path.join(self.playground, 'foo')
        os.chmod(self.playground, 0000)
        self.addCleanup(os.chmod, self.playground, 0700)
        with self.assertRaises(OSError):
            utils.mkdir(os.path.join(path))
        self.assertFalse(os.path.exists(path))


class TestParseBundle(
        helpers.BundleFileTestsMixin, helpers.ValueErrorTestsMixin,
        unittest.TestCase):

    def assert_bundle(
            self, expected_name, expected_services, contents,
            bundle_name=None):
        """Ensure parsing the given contents returns the expected values."""
        name, services = utils.parse_bundle(contents, bundle_name=bundle_name)
        self.assertEqual(expected_name, name)
        self.assertEqual(set(expected_services), set(services))

    def test_invalid_yaml(self):
        # A ValueError is raised if the bundle contents are not a valid YAML.
        with self.assertRaises(ValueError) as context_manager:
            utils.parse_bundle(':')
        expected = 'unable to parse the bundle'
        self.assertIn(expected, bytes(context_manager.exception))

    def test_yaml_invalid_type(self):
        # A ValueError is raised if the bundle contents are not well formed.
        with self.assert_value_error('invalid YAML contents: a-string'):
            utils.parse_bundle('a-string')

    def test_yaml_invalid_bundle_data(self):
        # A ValueError is raised if bundles are not well formed.
        contents = yaml.safe_dump({'mybundle': 'not valid'})
        expected = 'invalid YAML contents: {mybundle: not valid}\n'
        with self.assert_value_error(expected):
            utils.parse_bundle(contents)

    def test_yaml_no_service(self):
        # A ValueError is raised if bundles do not include services.
        contents = yaml.safe_dump({'mybundle': {}})
        expected = 'invalid YAML contents: mybundle: {}\n'
        with self.assert_value_error(expected):
            utils.parse_bundle(contents)

    def test_yaml_none_bundle_services(self):
        # A ValueError is raised if services are None.
        contents = yaml.safe_dump({'mybundle': {'services': None}})
        expected = 'invalid YAML contents: mybundle: {services: null}\n'
        with self.assert_value_error(expected):
            utils.parse_bundle(contents)

    def test_yaml_invalid_bundle_services_type(self):
        # A ValueError is raised if services have an invalid type.
        contents = yaml.safe_dump({'mybundle': {'services': 42}})
        expected = 'invalid YAML contents: mybundle: {services: 42}\n'
        with self.assert_value_error(expected):
            utils.parse_bundle(contents)

    def test_yaml_no_bundles(self):
        # A ValueError is raised if the bundle contents are empty.
        with self.assert_value_error('no bundles found'):
            utils.parse_bundle(yaml.safe_dump({}))

    def test_bundle_name_not_specified(self):
        # A ValueError is raised if the bundle name is not specified and the
        # contents contain more than one bundle.
        expected = ('multiple bundles found (bundle1, bundle2) '
                    'but no bundle name specified')
        with self.assert_value_error(expected):
            utils.parse_bundle(self.valid_bundle)

    def test_bundle_name_not_found(self):
        # A ValueError is raised if the given bundle is not found in the file.
        expected = ('bundle no-such not found in the provided list of bundles '
                    '(bundle1, bundle2)')
        with self.assert_value_error(expected):
            utils.parse_bundle(self.valid_bundle, 'no-such')

    def test_no_services(self):
        # A ValueError is raised if the specified bundle does not contain
        # services.
        contents = yaml.safe_dump({'mybundle': {'services': {}}})
        expected = 'bundle mybundle does not include any services'
        with self.assert_value_error(expected):
            utils.parse_bundle(contents)

    def test_yaml_gui_in_services(self):
        # A ValueError is raised if the bundle contains juju-gui.
        contents = yaml.safe_dump({
            'mybundle': {'services': {settings.JUJU_GUI_SERVICE_NAME: {}}},
        })
        expected = 'bundle mybundle contains an instance of juju-gui. ' \
            'quickstart will install the latest version of the Juju GUI ' \
            'automatically, please remove juju-gui from the bundle.'
        with self.assert_value_error(expected):
            utils.parse_bundle(contents)

    def test_success_no_name(self):
        # The function succeeds when an implicit bundle name is used.
        contents = yaml.safe_dump({
            'mybundle': {'services': {'wordpress': {}, 'mysql': {}}},
        })
        self.assert_bundle('mybundle', ['mysql', 'wordpress'], contents)

    def test_success_multiple_bundles(self):
        # The function succeeds with multiple bundles.
        self.assert_bundle(
            'bundle2', ['django', 'nodejs'], self.valid_bundle, 'bundle2')

    def test_success_json(self):
        # Since JSON is a subset of YAML, the function also support JSON
        # encoded bundles.
        contents = json.dumps({
            'mybundle': {'services': {'wordpress': {}, 'mysql': {}}},
        })
        self.assert_bundle('mybundle', ['mysql', 'wordpress'], contents)


class TestParseStatusOutput(helpers.ValueErrorTestsMixin, unittest.TestCase):

    def test_invalid_yaml(self):
        # A ValueError is raised if the output is not a valid YAML.
        with self.assertRaises(ValueError) as context_manager:
            utils.parse_status_output(':')
        expected = 'unable to parse the output'
        self.assertIn(expected, bytes(context_manager.exception))

    def test_invalid_yaml_contents(self):
        # A ValueError is raised if the output is not well formed.
        with self.assert_value_error('invalid YAML contents: a-string'):
            utils.parse_status_output('a-string')

    def test_no_agent_state(self):
        # A ValueError is raised if the agent-state is not found in the YAML.
        data = {
            'machines': {
                '0': {'agent-version': '1.17.0.1'},
            },
        }
        expected = 'machines:0:agent-state not found in {}'.format(bytes(data))
        with self.assert_value_error(expected):
            utils.get_agent_state(yaml.safe_dump(data))

    def test_success_agent_state(self):
        # The agent state is correctly returned.
        output = yaml.safe_dump({
            'machines': {
                '0': {'agent-version': '1.17.0.1', 'agent-state': 'started'},
            },
        })
        agent_state = utils.get_agent_state(output)
        self.assertEqual('started', agent_state)

    def test_no_bootstrap_node_series(self):
        # A ValueError is raised if the series is not found in the YAML.
        data = {
            'machines': {
                '0': {'agent-version': '1.17.0.1'},
            },
        }
        expected = 'machines:0:series not found in {}'.format(bytes(data))
        with self.assert_value_error(expected):
            utils.get_bootstrap_node_series(yaml.safe_dump(data))

    def test_success_bootstrap_node_series(self):
        # The bootstrap node series is correctly returned.
        output = yaml.safe_dump({
            'machines': {
                '0': {'agent-version': '1.17.0.1',
                      'agent-state': 'started',
                      'series': 'zydeco'},
            },
        })
        bsn_series = utils.get_bootstrap_node_series(output)
        self.assertEqual('zydeco', bsn_series)


class TestRunOnce(unittest.TestCase):

    def setUp(self):
        self.results = []
        self.func = utils.run_once(self.results.append)

    def test_runs_once(self):
        # The wrapped function runs only the first time it is invoked.
        self.func(1)
        self.assertEqual([1], self.results)
        self.func(2)
        self.assertEqual([1], self.results)

    def test_wrapped(self):
        # The wrapped function looks like the original one.
        self.assertEqual('append', self.func.__name__)
        self.assertEqual(list.append.__doc__, self.func.__doc__)


class TestGetJujuVersion(
        helpers.CallTestsMixin, helpers.ValueErrorTestsMixin,
        unittest.TestCase):

    def test_return_deconstructed_version(self):
        # Should return a deconstructed juju version.
        with self.patch_call(0, '1.17.1-precise-amd64\n', ''):
            version = utils.get_juju_version('juju')
        self.assertEqual((1, 17, 1), version)

    def test_juju_version_error(self):
        # A ValueError is raised if "juju version" exits with an error.
        with self.patch_call(1, 'foo', 'bad wolf'):
            with self.assert_value_error('bad wolf'):
                utils.get_juju_version('juju')

    def test_alpha_version_string(self):
        # Patch level defaults to zero.
        with self.patch_call(0, '1.17-alpha1-precise-amd64', ''):
            version = utils.get_juju_version('juju')
        self.assertEqual((1, 17, 0), version)

    def test_invalid_version_string(self):
        # A ValueError is raised if "juju version" outputs an invalid version.
        with self.patch_call(0, '1-precise-amd64', ''):
            with self.assert_value_error('invalid version string: 1'):
                utils.get_juju_version('juju')
