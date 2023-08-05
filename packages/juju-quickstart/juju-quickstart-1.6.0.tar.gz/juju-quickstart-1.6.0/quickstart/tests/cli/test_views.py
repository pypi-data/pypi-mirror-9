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

"""Tests for the Juju Quickstart CLI application views."""

from __future__ import unicode_literals

from contextlib import (
    contextmanager,
    nested,
)
import unittest

import mock
import urwid

from quickstart import settings
from quickstart.cli import (
    base,
    forms,
    params,
    ui,
    views,
)
from quickstart.models import (
    envs,
    jenv,
)
from quickstart.tests import helpers
from quickstart.tests.cli import helpers as cli_helpers


MAAS_NAME = 'maas-name'
MAAS_SERVER = 'http://1.2.3.4/MAAS'
MAAS_API_KEY = 'maas-secret'


def local_envs_supported(value):
    """Simulate local environments support in the current platform.

    The value argument is a boolean representing whether or not local
    environments are supported.
    Return a context manager that can be used when calling views.
    """
    return mock.patch(
        'quickstart.cli.views.platform_support.supports_local',
        mock.Mock(return_value=value))


def maas_env_detected(value):
    """Simulate whether a logged in MAAS remote API has been detected.

    The value argument is a boolean representing whether or not a MAAS API
    is available. If available, also patch "maas list" to return the following
    default values: MAAS_NAME, MAAS_SERVER and MAAS_API_KEY.
    Return a context manager that can be used when calling views.
    """
    patch_cli_available = mock.patch(
        'quickstart.cli.views.maas.cli_available',
        mock.Mock(return_value=value))
    if value:
        return_value = (MAAS_NAME, MAAS_SERVER, MAAS_API_KEY)
        patch_get_api_info = mock.patch(
            'quickstart.cli.views.maas.get_api_info',
            mock.Mock(return_value=return_value))
        return nested(patch_cli_available, patch_get_api_info)
    return patch_cli_available


class TestShow(unittest.TestCase):

    @contextmanager
    def patch_setup_urwid_app(self, run_side_effect=None):
        """Patch the base.setup_urwid_app function.

        The context manager returns a tuple (mock_loop, mock_app) containing
        the two mock objects returned by the mock call.

        The run_side_effect argument can be provided to specify the side
        effects of the mock_loop.run call.
        """
        mock_loop = mock.Mock()
        mock_loop.run = mock.Mock(side_effect=run_side_effect)
        mock_setup_urwid_app = mock.Mock(return_value=(mock_loop, mock.Mock()))
        setup_urwid_app_path = 'quickstart.cli.views.base.setup_urwid_app'
        with mock.patch(setup_urwid_app_path, mock_setup_urwid_app):
            yield mock_setup_urwid_app()

    def test_show_view(self):
        # The loop and app objects are properly used by the show function:
        # the loop is run and the app is passed to the view.
        view = mock.Mock()
        with self.patch_setup_urwid_app() as (mock_loop, mock_app):
            views.show(view)
        view.assert_called_once_with(mock_app)
        mock_loop.run.assert_called_once_with()

    def test_view_exit(self):
        # An ui.AppExit correctly quits the application. The return value
        # encapsulated on the exception is also returned by the show function.
        view = mock.Mock()
        run_side_effect = ui.AppExit('bad wolf')
        with self.patch_setup_urwid_app(run_side_effect=run_side_effect):
            with helpers.mock_print as mock_print:
                return_value = views.show(view)
        self.assertEqual('bad wolf', return_value)
        mock_print.assert_called_once_with('interactive session closed')

    def test_view_arguments(self):
        # The view is invoked passing the app and all the optional show
        # function arguments.
        view = mock.Mock()
        with self.patch_setup_urwid_app() as (mock_loop, mock_app):
            views.show(view, 'arg1', 'arg2')
        view.assert_called_once_with(mock_app, 'arg1', 'arg2')


class EnvViewTestsMixin(cli_helpers.CliAppTestsMixin):
    """Shared helpers for testing environment views."""

    env_type_db = envs.get_env_type_db()

    def setUp(self):
        # Set up the base Urwid application.
        self.loop, self.app = base.setup_urwid_app()
        self.save_callable = mock.Mock()
        self.remove_jenv_callable = mock.Mock(return_value=None)

    def get_widgets_in_contents(self, filter_function=None):
        """Return a list of widgets included in the app contents.

        Use the filter_function argument to filter the returned list.
        """
        contents = self.app.get_contents()
        return filter(filter_function, list(contents.base_widget.body))

    def get_control_buttons(self):
        """Return the list of buttons included in a control box.

        Control boxes are created using ui.create_controls().
        """
        piles = self.get_widgets_in_contents(
            filter_function=self.is_a(urwid.Pile))
        # Assume the control box is the last Pile.
        controls = piles[-1]
        # The button columns is the second widget in the Pile.
        columns = controls.contents[1][0].base_widget
        return [content[0].base_widget for content in columns.contents]

    def is_a(self, cls):
        """Return a function returning True if the given argument is a cls.

        The resulting function can be used as the filter_function argument in
        self.get_widgets_in_contents() calls.
        """
        return lambda arg: isinstance(arg, cls)

    def make_params(self, env_db, jenv_db):
        """Create and return view parameters using the given env databases."""
        return params.Params(
            env_type_db=self.env_type_db,
            env_db=env_db,
            jenv_db=jenv_db,
            save_callable=self.save_callable,
            remove_jenv_callable=self.remove_jenv_callable,
        )

    def click_remove_button(self, env_name):
        """Click the remove button in an environment detail view.

        Assume the view was already called.
        Return the dialog button widgets and the original view contents.
        """
        original_contents = self.app.get_contents()
        # The "remove" button is the last one.
        remove_button = self.get_control_buttons()[-1]
        cli_helpers.emit(remove_button)
        # The original env detail contents have been replaced.
        contents = self.app.get_contents()
        self.assertIsNot(contents, original_contents)
        # A "remove" confirmation dialog is displayed.
        title_widget, message_widget, buttons = cli_helpers.inspect_dialog(
            contents)
        self.assertEqual(
            'Remove the {} environment'.format(env_name), title_widget.text)
        self.assertEqual('This action cannot be undone!', message_widget.text)
        return buttons, original_contents

    def cancel_removal(self, env_name):
        """Cancel the environment deletion by clicking the "cancel" button."""
        buttons, original_contents = self.click_remove_button(env_name)
        # The "cancel" button is the first one in the dialog.
        cancel_button = buttons[0]
        cli_helpers.emit(cancel_button)
        return original_contents

    def confirm_removal(self, env_name):
        """Confirm the environment deletion."""
        buttons, _ = self.click_remove_button(env_name)
        # The "confirm" button is the second one in the dialog.
        confirm_button = buttons[1]
        cli_helpers.emit(confirm_button)


class TestEnvIndex(EnvViewTestsMixin, unittest.TestCase):

    base_status = ' \N{UPWARDS ARROW LEFTWARDS OF DOWNWARDS ARROW} navigate '
    create_local_caption = (
        '\N{BULLET} automatically create and bootstrap a local environment')
    create_maas_caption = (
        '\N{BULLET} automatically create and bootstrap the {} MAAS '
        'environment'.format(MAAS_NAME))
    active_environments_message = 'Other active environments'

    def test_view_default_return_value_on_exit(self):
        # The view configures the app so that the return value on user exit is
        # a tuple including a copy of the given env_db and None, the latter
        # meaning no environment has been selected.
        env_db = helpers.make_env_db()
        jenv_db = helpers.make_jenv_db()
        views.env_index(self.app, self.make_params(env_db, jenv_db))
        new_env_db, env_data = self.get_on_exit_return_value(self.loop)
        self.assertEqual(env_db, new_env_db)
        self.assertIsNot(env_db, new_env_db)
        self.assertIsNone(env_data)

    def test_view_title(self):
        # The application title is correctly set up.
        env_db = helpers.make_env_db()
        jenv_db = helpers.make_jenv_db()
        views.env_index(self.app, self.make_params(env_db, jenv_db))
        self.assertEqual(
            'Select an existing Juju environment or create a new one',
            self.app.get_title())

    def test_view_title_no_environments(self):
        # The application title changes if the env_db has no environments.
        env_db = {'environments': {}}
        jenv_db = helpers.make_jenv_db()
        views.env_index(self.app, self.make_params(env_db, jenv_db))
        self.assertEqual(
            'No Juju environments already set up: please create one',
            self.app.get_title())

    def test_view_contents(self):
        # The view displays a list of the environments in env_db, and buttons
        # to create new environments.
        env_db = helpers.make_env_db()
        jenv_db = {'environments': {}}
        with local_envs_supported(True):
            views.env_index(self.app, self.make_params(env_db, jenv_db))
        buttons = self.get_widgets_in_contents(
            filter_function=self.is_a(ui.MenuButton))
        # A button is created for each existing environment (see details) and
        # for each environment type supported by quickstart (create).
        env_types = envs.get_supported_env_types(self.env_type_db)
        expected_buttons_number = len(env_db['environments']) + len(env_types)
        self.assertEqual(expected_buttons_number, len(buttons))

    def test_view_contents_with_imported_envs(self):
        # The view displays a list of active imported environments, and buttons
        # to create new environments.
        env_db = {'environments': {}}
        jenv_db = helpers.make_jenv_db()
        with local_envs_supported(True):
            views.env_index(self.app, self.make_params(env_db, jenv_db))
        buttons = self.get_widgets_in_contents(
            filter_function=self.is_a(ui.MenuButton))
        # A button is created for each existing environment (see details) and
        # for each environment type supported by quickstart (create).
        env_types = envs.get_supported_env_types(self.env_type_db)
        expected_buttons_number = (
            # The number of active environments.
            len(jenv_db['environments']) +
            # The buttons to create new environments.
            len(env_types) +
            # The button to automatically create a new local environment.
            1
        )
        self.assertEqual(expected_buttons_number, len(buttons))
        # A text widget is displayed as header for the imported environments.
        widgets = self.get_widgets_in_contents(
            filter_function=self.is_a(urwid.Text))
        self.assertEqual(self.active_environments_message, widgets[2].text)

    def test_view_contents_without_imported_envs(self):
        # If there are no active imported environments the corresponding
        # header text is not displayed.
        env_db = jenv_db = {'environments': {}}
        views.env_index(self.app, self.make_params(env_db, jenv_db))
        widgets = self.get_widgets_in_contents(
            filter_function=self.is_a(urwid.Text))
        texts = [widget.text for widget in widgets]
        self.assertNotIn(self.active_environments_message, texts)

    def test_new_local_environment_disabled(self):
        # The option to create a new local environment is not present if they
        # are not supported in the current platform.
        env_db = helpers.make_env_db()
        jenv_db = helpers.make_jenv_db()
        with local_envs_supported(False):
            views.env_index(self.app, self.make_params(env_db, jenv_db))
        buttons = self.get_widgets_in_contents(
            filter_function=self.is_a(ui.MenuButton))
        captions = map(cli_helpers.get_button_caption, buttons)
        create_local_captions = [
            caption for caption in captions
            if caption.startswith('\N{BULLET} new local')
        ]
        self.assertEqual([], create_local_captions)

    @mock.patch('quickstart.cli.views.env_detail')
    def test_environment_clicked(self, mock_env_detail):
        # The environment detail view is called when clicking an environment.
        env_db = helpers.make_env_db()
        jenv_db = {'environments': {}}
        params = self.make_params(env_db, jenv_db)
        views.env_index(self.app, params)
        buttons = self.get_widgets_in_contents(
            filter_function=self.is_a(ui.MenuButton))
        # The environments are listed in alphabetical order.
        environments = sorted(env_db['environments'])
        for env_name, button in zip(environments, buttons):
            env_data = envs.get_env_data(env_db, env_name)
            # The caption includes the environment description.
            env_description = envs.get_env_short_description(env_data)
            self.assertIn(
                env_description, cli_helpers.get_button_caption(button))
            # When the button is clicked, the detail view is called passing the
            # corresponding environment data.
            cli_helpers.emit(button)
            mock_env_detail.assert_called_once_with(self.app, params, env_data)
            # Reset the mock so that it does not include any calls on the next
            # loop cycle.
            mock_env_detail.reset_mock()

    @mock.patch('quickstart.cli.views.jenv_detail')
    def test_imported_environment_clicked(self, mock_jenv_detail):
        # The jenv detail view is called when clicking an imported environment.
        env_db = {'environments': {}}
        jenv_db = helpers.make_jenv_db()
        params = self.make_params(env_db, jenv_db)
        with local_envs_supported(False):
            views.env_index(self.app, params)
        buttons = self.get_widgets_in_contents(
            filter_function=self.is_a(ui.MenuButton))
        # The environments are listed in alphabetical order.
        environments = sorted(jenv_db['environments'])
        for env_name, button in zip(environments, buttons):
            env_data = envs.get_env_data(jenv_db, env_name)
            # The caption includes the environment description.
            env_description = jenv.get_env_short_description(env_data)
            self.assertIn(
                env_description, cli_helpers.get_button_caption(button))
            # When the button is clicked, the jenv detail view is called
            # passing the corresponding environment data.
            cli_helpers.emit(button)
            mock_jenv_detail.assert_called_once_with(
                self.app, params, env_data)
            # Reset the mock so that it does not include any calls on the next
            # loop cycle.
            mock_jenv_detail.reset_mock()

    @mock.patch('quickstart.cli.views.env_edit')
    def test_create_new_environment_clicked(self, mock_env_edit):
        # The environment edit view is called when clicking to create a new
        # environment.
        env_db = helpers.make_env_db()
        jenv_db = {'environments': {}}
        params = self.make_params(env_db, jenv_db)
        with local_envs_supported(True):
            views.env_index(self.app, params)
        buttons = self.get_widgets_in_contents(
            filter_function=self.is_a(ui.MenuButton))
        env_types = envs.get_supported_env_types(self.env_type_db)
        for type_tuple, button in zip(env_types, buttons[-len(env_types):]):
            env_type, label = type_tuple
            # The caption includes the environment type label.
            expected_caption = 'new {} environment'.format(label)
            caption = cli_helpers.get_button_caption(button)
            self.assertIn(expected_caption, caption)
            # When the button is clicked, the edit view is called passing the
            # corresponding environment data.
            cli_helpers.emit(button)
            mock_env_edit.assert_called_once_with(
                self.app, params, {
                    'type': env_type,
                    'default-series': settings.JUJU_GUI_SUPPORTED_SERIES[-1],
                })
            # Reset the mock so that it does not include any calls on the next
            # loop cycle.
            mock_env_edit.reset_mock()

    def test_create_and_bootstrap_local_environment_clicked(self):
        # When there are no environments in the env_db the view exposes an
        # option to automatically create and bootstrap a new local environment.
        # If that option is clicked, the view quits the application returning
        # the newly created env_data.
        env_db = envs.create_empty_env_db()
        jenv_db = helpers.make_jenv_db()
        with maas_env_detected(False):
            with local_envs_supported(True):
                views.env_index(self.app, self.make_params(env_db, jenv_db))
        buttons = self.get_widgets_in_contents(
            filter_function=self.is_a(ui.MenuButton))
        # The "create and bootstrap" button is the first one in the contents.
        create_button = buttons[0]
        self.assertEqual(
            self.create_local_caption,
            cli_helpers.get_button_caption(create_button))
        # An AppExit is raised clicking the button.
        with self.assertRaises(ui.AppExit) as context_manager:
            cli_helpers.emit(create_button)
        new_env_db, env_data = context_manager.exception.return_value
        # The environments database is no longer empty.
        self.assertIn('local', new_env_db['environments'])
        self.assertEqual(envs.get_env_data(new_env_db, 'local'), env_data)

    def test_create_and_bootstrap_local_environment_missing(self):
        # The option to automatically create and bootstrap a new local
        # environment is not displayed if the current platform does not support
        # local environments.
        env_db = envs.create_empty_env_db()
        jenv_db = helpers.make_jenv_db()
        with local_envs_supported(False):
            views.env_index(self.app, self.make_params(env_db, jenv_db))
        buttons = self.get_widgets_in_contents(
            filter_function=self.is_a(ui.MenuButton))
        # No "create and bootstrap local" buttons are present.
        captions = map(cli_helpers.get_button_caption, buttons)
        self.assertNotIn(self.create_local_caption, captions)

    def test_create_and_bootstrap_maas_environment_clicked(self):
        # When there are no environments in the env_db and a remote MAAS API is
        # detected, the view exposes an option to automatically create and
        # bootstrap a new MAAS environment.
        # If that option is clicked, the view quits the application returning
        # the newly created env_data.
        env_db = envs.create_empty_env_db()
        jenv_db = helpers.make_jenv_db()
        with maas_env_detected(True):
            views.env_index(self.app, self.make_params(env_db, jenv_db))
        buttons = self.get_widgets_in_contents(
            filter_function=self.is_a(ui.MenuButton))
        # The "create and bootstrap" button is the first one in the contents.
        create_button = buttons[0]
        self.assertEqual(
            self.create_maas_caption,
            cli_helpers.get_button_caption(create_button))
        # An AppExit is raised clicking the button.
        with self.assertRaises(ui.AppExit) as context_manager:
            cli_helpers.emit(create_button)
        new_env_db, env_data = context_manager.exception.return_value
        # The environments database is no longer empty.
        self.assertIn(MAAS_NAME, new_env_db['environments'])
        self.assertEqual(envs.get_env_data(new_env_db, MAAS_NAME), env_data)

    def test_create_and_bootstrap_maas_environment_missing(self):
        # The option to automatically create and bootstrap a new MAAS
        # environment is not displayed if no MAAS API endpoints are
        # available on the system
        env_db = envs.create_empty_env_db()
        jenv_db = helpers.make_jenv_db()
        with maas_env_detected(False):
            views.env_index(self.app, self.make_params(env_db, jenv_db))
        buttons = self.get_widgets_in_contents(
            filter_function=self.is_a(ui.MenuButton))
        # No "create and bootstrap MAAS" buttons are present.
        captions = map(cli_helpers.get_button_caption, buttons)
        self.assertNotIn(self.create_maas_caption, captions)

    def test_selected_environment(self):
        # The default environment is already selected in the list.
        env_db = helpers.make_env_db(default='lxc')
        jenv_db = helpers.make_jenv_db()
        views.env_index(self.app, self.make_params(env_db, jenv_db))
        env_data = envs.get_env_data(env_db, 'lxc')
        env_description = envs.get_env_short_description(env_data)
        contents = self.app.get_contents()
        focused_widget = contents.get_focus()[0]
        self.assertIsInstance(focused_widget, ui.MenuButton)
        self.assertIn(
            env_description, cli_helpers.get_button_caption(focused_widget))

    def test_status_with_errors(self):
        # The status message explains how errors are displayed.
        env_db = helpers.make_env_db()
        jenv_db = {'environments': {}}
        views.env_index(self.app, self.make_params(env_db, jenv_db))
        status = self.app.get_status()
        self.assertEqual(self.base_status + ' \N{BULLET} has errors ', status)

    def test_status_with_default(self):
        # The status message explains how default environment is represented.
        env_db = helpers.make_env_db(default='lxc', exclude_invalid=True)
        jenv_db = {'environments': {}}
        views.env_index(self.app, self.make_params(env_db, jenv_db))
        status = self.app.get_status()
        self.assertEqual(self.base_status + ' \N{CHECK MARK} default ', status)

    def test_status_with_active(self):
        # The status message explains how active environments are displayed.
        env_db = helpers.make_env_db(exclude_invalid=True)
        jenv_db = helpers.make_jenv_db()
        views.env_index(self.app, self.make_params(env_db, jenv_db))
        status = self.app.get_status()
        self.assertEqual(self.base_status + ' \N{BULLET} active ', status)

    def test_complete_status(self):
        # The status message includes default, active and errors explanations.
        env_db = helpers.make_env_db(default='lxc')
        jenv_db = helpers.make_jenv_db()
        views.env_index(self.app, self.make_params(env_db, jenv_db))
        status = self.app.get_status()
        self.assertEqual(
            self.base_status +
            ' \N{CHECK MARK} default ' +
            ' \N{BULLET} active ' +
            ' \N{BULLET} has errors ',
            status)

    def test_base_status(self):
        # The status only includes navigation info if there are no errors.
        env_db = helpers.make_env_db(exclude_invalid=True)
        jenv_db = {'environments': {}}
        views.env_index(self.app, self.make_params(env_db, jenv_db))
        status = self.app.get_status()
        self.assertEqual(self.base_status, status)


class TestEnvDetail(EnvViewTestsMixin, unittest.TestCase):

    base_status = ' \N{RIGHTWARDS ARROW OVER LEFTWARDS ARROW} navigate '
    env_db = helpers.make_env_db(default='lxc')
    jenv_db = helpers.make_jenv_db()

    def call_view(self, env_name='lxc'):
        """Call the view passing the env_data corresponding to env_name."""
        self.env_data = envs.get_env_data(self.env_db, env_name)
        self.params = self.make_params(self.env_db, self.jenv_db)
        return views.env_detail(self.app, self.params, self.env_data)

    def test_view_default_return_value_on_exit(self):
        # The view configures the app so that the return value on user exit is
        # a tuple including a copy of the given env_db and None, the latter
        # meaning no environment has been selected (for now).
        self.call_view()
        new_env_db, env_data = self.get_on_exit_return_value(self.loop)
        self.assertEqual(self.env_db, new_env_db)
        self.assertIsNot(self.env_db, new_env_db)
        self.assertIsNone(env_data)

    def test_view_title(self):
        # The application title is correctly set up: it shows the description
        # of the current environment.
        self.call_view()
        env_description = envs.get_env_short_description(self.env_data)
        self.assertEqual(env_description, self.app.get_title())

    def test_view_contents(self):
        # The view displays a list of the environment fields.
        self.call_view()
        widgets = self.get_widgets_in_contents(
            filter_function=self.is_a(urwid.Text))
        env_metadata = envs.get_env_metadata(self.env_type_db, self.env_data)
        expected_texts = [
            '{}: {}'.format(field.name, field.display(value)) for field, value
            in envs.map_fields_to_env_data(env_metadata, self.env_data)
            if field.required or (value is not None)
        ]
        for expected_text, widget in zip(expected_texts, widgets):
            self.assertEqual(expected_text, widget.text)

    def test_view_buttons(self):
        # The following buttons are displayed: "back", "use", "set default",
        # "edit" and "remove".
        self.call_view(env_name='ec2-west')
        buttons = self.get_control_buttons()
        captions = map(cli_helpers.get_button_caption, buttons)
        self.assertEqual(
            ['back', 'use', 'set default', 'edit', 'remove'], captions)

    def test_view_buttons_default(self):
        # If the environment is the default one, the "set default" button is
        # not displayed. The buttons we expect are "back", "use", "edit" and
        # "remove".
        self.call_view(env_name='lxc')
        buttons = self.get_control_buttons()
        captions = map(cli_helpers.get_button_caption, buttons)
        self.assertEqual(['back', 'use', 'edit', 'remove'], captions)

    def test_view_buttons_error(self):
        # If the environment is not valid, the "use" button is not displayed.
        # The buttons we expect are "back", "set default", "edit" and "remove".
        self.call_view(env_name='local-with-errors')
        buttons = self.get_control_buttons()
        captions = map(cli_helpers.get_button_caption, buttons)
        self.assertEqual(['back', 'set default', 'edit', 'remove'], captions)

    @mock.patch('quickstart.cli.views.env_index')
    def test_back_button(self, mock_env_index):
        # The index view is called if the "back" button is clicked.
        self.call_view(env_name='ec2-west')
        # The "back" button is the first one.
        back_button = self.get_control_buttons()[0]
        cli_helpers.emit(back_button)
        mock_env_index.assert_called_once_with(self.app, self.params)

    def test_use_button(self):
        # The application exits if the "use" button is clicked.
        # The env_db and the current environment data are returned.
        self.call_view(env_name='ec2-west')
        # The "use" button is the second one.
        use_button = self.get_control_buttons()[1]
        with self.assertRaises(ui.AppExit) as context_manager:
            cli_helpers.emit(use_button)
        expected_return_value = (self.env_db, self.env_data)
        self.assertEqual(
            expected_return_value, context_manager.exception.return_value)

    @mock.patch('quickstart.cli.views.env_index')
    def test_set_default_button(self, mock_env_index):
        # The current environment is set as default if the "set default" button
        # is clicked. Subsequently the application switches to the index view.
        self.call_view(env_name='ec2-west')
        # The "set default" button is the third one.
        set_default_button = self.get_control_buttons()[2]
        cli_helpers.emit(set_default_button)
        # The index view has been called passing the modified env_db in params.
        self.assertTrue(mock_env_index.called)
        params = mock_env_index.call_args[0][1]
        # The new env_db has a new default.
        self.assertEqual(params.env_db['default'], 'ec2-west')
        # The new env_db has been saved.
        self.save_callable.assert_called_once_with(params.env_db)

    @mock.patch('quickstart.cli.views.env_edit')
    def test_edit_button(self, mock_env_edit):
        # The edit view is called if the "edit" button is clicked.
        self.call_view(env_name='ec2-west')
        # The "edit" button is the fourth one.
        edit_button = self.get_control_buttons()[3]
        cli_helpers.emit(edit_button)
        mock_env_edit.assert_called_once_with(
            self.app, self.params, self.env_data)

    def test_remove_button(self):
        # A confirmation dialog is displayed if the "remove" button is clicked.
        self.call_view(env_name='ec2-west')
        buttons, _ = self.click_remove_button('ec2-west')
        # The dialog includes the "cancel" and "confirm" buttons.
        self.assertEqual(2, len(buttons))
        captions = map(cli_helpers.get_button_caption, buttons)
        self.assertEqual(['cancel', 'confirm'], captions)

    def test_remove_cancelled(self):
        # The "remove" confirmation dialog can be safely dismissed.
        self.call_view(env_name='ec2-west')
        original_contents = self.cancel_removal('ec2-west')
        # The original contents have been restored.
        self.assertIs(original_contents, self.app.get_contents())

    @mock.patch('quickstart.cli.views.env_index')
    def test_remove_confirmed(self, mock_env_index):
        # The current environment is removed if the "remove" button is clicked
        # and then the deletion is confirmed. Subsequently the application
        # switches to the index view.
        env_name = 'ec2-west'
        self.call_view(env_name=env_name)
        self.confirm_removal(env_name)
        # A message notifies the environment has been removed.
        self.assertEqual(
            '{} successfully removed'.format(env_name), self.app.get_message())
        # The index view has been called passing the modified env_db in params.
        self.assertTrue(mock_env_index.called)
        params = mock_env_index.call_args[0][1]
        # The new env_db no longer includes the "ec2-west" environment.
        self.assertNotIn(env_name, params.env_db['environments'])
        # The new env_db has been saved.
        self.save_callable.assert_called_once_with(params.env_db)

    def test_status_with_errors(self):
        # The status message explains how field errors are displayed.
        self.call_view(env_name='local-with-errors')
        status = self.app.get_status()
        self.assertEqual(
            self.base_status + ' \N{LOWER SEVEN EIGHTHS BLOCK} field error ',
            status)

    def test_status_without_errors(self):
        # The status only includes navigation info if there are no errors.
        self.call_view(env_name='lxc')
        status = self.app.get_status()
        self.assertEqual(self.base_status, status)


class TestJenvDetail(EnvViewTestsMixin, unittest.TestCase):

    env_db = helpers.make_env_db(default='lxc')
    jenv_db = helpers.make_jenv_db()

    def call_view(self, env_name='lxc'):
        """Call the view passing the env_data corresponding to env_name."""
        self.env_data = envs.get_env_data(self.jenv_db, env_name)
        self.params = self.make_params(self.env_db, self.jenv_db)
        return views.jenv_detail(self.app, self.params, self.env_data)

    def test_view_default_return_value_on_exit(self):
        # The view configures the app so that the return value on user exit is
        # a tuple including a copy of the given env_db and None, the latter
        # meaning no environment has been selected (for now).
        self.call_view()
        new_env_db, env_data = self.get_on_exit_return_value(self.loop)
        self.assertEqual(self.env_db, new_env_db)
        self.assertIsNot(self.env_db, new_env_db)
        self.assertIsNone(env_data)

    def test_view_title(self):
        # The application title is correctly set up: it shows the description
        # of the current jenv environment.
        self.call_view()
        env_description = jenv.get_env_short_description(self.env_data)
        self.assertEqual(env_description, self.app.get_title())

    def test_view_contents(self):
        # The view displays the jenv details.
        self.call_view()
        widgets = self.get_widgets_in_contents(
            filter_function=self.is_a(urwid.Text))
        expected_texts = [
            '{}: {}'.format(label, value) for label, value
            in jenv.get_env_details(self.env_data)
        ]
        for expected_text, widget in zip(expected_texts, widgets):
            self.assertEqual(expected_text, widget.text)

    def test_view_buttons(self):
        # The "back", "use" and "remove" buttons are displayed.
        self.call_view(env_name='ec2-west')
        buttons = self.get_control_buttons()
        captions = map(cli_helpers.get_button_caption, buttons)
        self.assertEqual(['back', 'use', 'remove'], captions)

    @mock.patch('quickstart.cli.views.env_index')
    def test_back_button(self, mock_env_index):
        # The index view is called if the "back" button is clicked.
        self.call_view(env_name='ec2-west')
        # The "back" button is the first one.
        back_button = self.get_control_buttons()[0]
        cli_helpers.emit(back_button)
        mock_env_index.assert_called_once_with(self.app, self.params)

    def test_use_button(self):
        # The application exits if the "use" button is clicked.
        # The env_db and the current environment data are returned.
        self.call_view(env_name='ec2-west')
        # The "use" button is the second one.
        use_button = self.get_control_buttons()[1]
        with self.assertRaises(ui.AppExit) as context_manager:
            cli_helpers.emit(use_button)
        expected_return_value = (self.env_db, self.env_data)
        self.assertEqual(
            expected_return_value, context_manager.exception.return_value)

    def test_remove_button(self):
        # A confirmation dialog is displayed if the "remove" button is clicked.
        self.call_view(env_name='test-jenv')
        buttons, _ = self.click_remove_button('test-jenv')
        # The dialog includes the "cancel" and "confirm" buttons.
        self.assertEqual(2, len(buttons))
        captions = map(cli_helpers.get_button_caption, buttons)
        self.assertEqual(['cancel', 'confirm'], captions)

    def test_remove_cancelled(self):
        # The "remove" confirmation dialog can be safely dismissed.
        self.call_view(env_name='test-jenv')
        original_contents = self.cancel_removal('test-jenv')
        # The original contents have been restored.
        self.assertIs(original_contents, self.app.get_contents())

    @mock.patch('quickstart.cli.views.env_index')
    def test_remove_confirmed(self, mock_env_index):
        # The jenv file is removed if the "remove" button is clicked and then
        # then the deletion is confirmed. Subsequently the application switches
        # to the index view.
        env_name = 'test-jenv'
        self.call_view(env_name=env_name)
        self.confirm_removal(env_name)
        # A message notifies the environment has been removed.
        self.assertEqual(
            '{} successfully removed'.format(env_name), self.app.get_message())
        # The index view has been called passing the modified jenv_db params.
        self.assertTrue(mock_env_index.called)
        params = mock_env_index.call_args[0][1]
        # The new jenv_db no longer includes the "test-jenv" environment.
        self.assertNotIn(env_name, params.jenv_db['environments'])
        # The corresponding jenv file has been removed.
        self.remove_jenv_callable.assert_called_once_with(env_name)
        self.assertEqual(
            'test-jenv successfully removed', self.app.get_message())

    @mock.patch('quickstart.cli.views.env_index')
    def test_remove_confirmed_error(self, mock_env_index):
        # Errors occurred while trying to remove the jenv files are notified.
        env_name = 'test-jenv'
        self.call_view(env_name=env_name)
        # Simulate an error removing the jenv file.
        self.remove_jenv_callable.return_value = 'bad wolf'
        self.confirm_removal(env_name)
        # The error is notified.
        self.assertEqual('bad wolf'.format(env_name), self.app.get_message())
        # The index view has been called passing the original jenv_db params.
        self.assertTrue(mock_env_index.called)
        params = mock_env_index.call_args[0][1]
        # The jenv_db still includes the "test_jenv" environment.
        self.assertIn(env_name, params.jenv_db['environments'])


class TestEnvEdit(EnvViewTestsMixin, unittest.TestCase):

    env_db = helpers.make_env_db(default='lxc')
    jenv_db = helpers.make_jenv_db()

    def call_view(self, env_name='lxc', env_type=None):
        """Call the view passing the env_data corresponding to env_name.

        If env_type is provided, the view is a creation form, env_name is
        ignored and a new env_data is passed to the view.
        """
        if env_type is None:
            self.env_data = envs.get_env_data(self.env_db, env_name)
        else:
            self.env_data = {'type': env_type}
        self.params = self.make_params(self.env_db, self.jenv_db)
        return views.env_edit(self.app, self.params, self.env_data)

    def get_form_contents(self):
        """Return the form contents included in the app page.

        The contents are returned as a sequence of (caption, value) tuples.
        """
        pile_widgets = self.get_widgets_in_contents(
            filter_function=self.is_a(urwid.Pile))
        form_contents = []
        for pile_widget in pile_widgets:
            base_widget = pile_widget.contents[0][0].base_widget
            if isinstance(base_widget, urwid.CheckBox):
                # This is a boolean widget.
                form_contents.append((
                    base_widget.label, base_widget.get_state()))
            elif hasattr(base_widget, 'contents'):
                # This is a string widget.
                caption = base_widget.contents[0][0].text
                value = base_widget.contents[1][0].get_edit_text()
                form_contents.append((caption, value))
        return form_contents

    def patch_create_form(self, changes=None):
        """Patch the forms.create_form function.

        The create_form function returns the form widgets and a callable
        returning the new env data. Make the latter return the current
        self.env_data instead, optionally updated using the given changes.
        """
        original_create_form = forms.create_form
        testcase = self

        class MockCreateForm(object):

            call_count = 0
            errors = None
            new_env_data = None

            def __call__(self, field_value_pairs, errors):
                self.call_count += 1
                self.errors = errors
                self.new_env_data = testcase.env_data.copy()
                if changes is not None:
                    self.new_env_data.update(changes)
                form_widgets, _ = original_create_form(
                    field_value_pairs, errors)
                return form_widgets, lambda: self.new_env_data

            @property
            def called(self):
                return bool(self.call_count)

        return mock.patch('quickstart.cli.forms.create_form', MockCreateForm())

    def test_view_default_return_value_on_exit(self):
        # The view configures the app so that the return value on user exit is
        # a tuple including a copy of the given env_db and None, the latter
        # meaning no environment has been selected (for now).
        self.call_view()
        new_env_db, env_data = self.get_on_exit_return_value(self.loop)
        self.assertEqual(self.env_db, new_env_db)
        self.assertIsNot(self.env_db, new_env_db)
        self.assertIsNone(env_data)

    def test_creation_view_title(self):
        # The application title is correctly set up when the view is used to
        # create a new environment.
        self.call_view(env_type='ec2')
        self.assertEqual('Create a new ec2 environment', self.app.get_title())

    def test_modification_view_title(self):
        # The application title is correctly set up when the view is used to
        # change an existing environment.
        self.call_view(env_name='lxc')
        self.assertEqual('Edit the local environment', self.app.get_title())

    def test_view_contents_description(self):
        # The view displays the provider description.
        self.call_view()
        text_widgets = self.get_widgets_in_contents(
            filter_function=self.is_a(urwid.Text))
        description = text_widgets[0]
        expected_description = self.env_type_db['local']['description']
        self.assertEqual(expected_description, description.text)

    def test_view_contents_form(self):
        # The view displays a form containing all the environment fields.
        self.call_view()
        expected_form_contents = [
            ('provider type: ', 'local'),
            ('environment name: ', 'lxc'),
            ('use lxc-clone', forms.MIXED),
            ('use lxc-clone-aufs', forms.MIXED),
            ('root dir: ', ''),
            ('storage port: ', '8888'),
            ('shared storage port: ', ''),
            ('network bridge: ', ''),
            ('admin secret: ', 'bones'),
            ('default series: ', 'raring'),
            ('default', True),
        ]
        self.assertEqual(expected_form_contents, self.get_form_contents())

    def test_view_buttons(self):
        # The following buttons are displayed: "save", "cancel" and "restore".
        self.call_view(env_name='ec2-west')
        buttons = self.get_control_buttons()
        captions = map(cli_helpers.get_button_caption, buttons)
        self.assertEqual(['save', 'cancel', 'restore'], captions)

    @mock.patch('quickstart.cli.views.env_detail')
    def test_save_button(self, mock_env_detail):
        # The new data is saved if the user clicks the save button.
        # Subsequently the user is redirected to the env detail view.
        changes = {'admin-secret': 'Secret!'}
        with self.patch_create_form(changes=changes) as mock_create_form:
            self.call_view(env_name='ec2-west')
        self.assertTrue(mock_create_form.called)
        # The "save" button is the first one.
        save_button = self.get_control_buttons()[0]
        cli_helpers.emit(save_button)
        # At this point the new env data should be normalized and saved into
        # the environments database.
        env_metadata = envs.get_env_metadata(self.env_type_db, self.env_data)
        new_env_data = envs.normalize(
            env_metadata, mock_create_form.new_env_data)
        envs.set_env_data(self.env_db, 'ec2-west', new_env_data)
        # The new data has been correctly saved.
        self.save_callable.assert_called_once_with(self.env_db)
        # A message notifies the environment has been saved.
        self.assertEqual(
            'ec2-west successfully modified', self.app.get_message())
        # The application displays the environment detail view.
        mock_env_detail.assert_called_once_with(
            self.app, self.params, new_env_data)

    @mock.patch('quickstart.cli.views.env_detail')
    def test_save_empty_db(self, mock_env_detail):
        # If the env_db is empty, the new environment is set as default.
        self.env_db = envs.create_empty_env_db()
        changes = {
            'name': 'lxc',
            'admin-secret': 'Secret!',
            'is-default': False,
        }
        with self.patch_create_form(changes=changes):
            self.call_view(env_type='local')
        save_button = self.get_control_buttons()[0]
        cli_helpers.emit(save_button)
        expected_new_env_data = changes.copy()
        expected_new_env_data.update({'type': 'local', 'is-default': True})
        envs.set_env_data(self.env_db, None, expected_new_env_data)
        mock_env_detail.assert_called_once_with(
            self.app, self.params, expected_new_env_data)

    def test_save_invalid_form_data(self):
        # Errors are displayed if the user tries to save invalid data.
        changes = {'name': ''}
        with self.patch_create_form(changes=changes) as mock_create_form:
            self.call_view(env_name='ec2-west')
            self.assertTrue(mock_create_form.called)
            # The "save" button is the first one.
            save_button = self.get_control_buttons()[0]
            cli_helpers.emit(save_button)
        # In case of errors, the save callable is not called.
        self.assertFalse(self.save_callable.called)
        # The form has been re-rendered passing the errors.
        self.assertEqual(2, mock_create_form.call_count)
        self.assertEqual(
            {'name': 'a value is required for the environment name field'},
            mock_create_form.errors)

    def test_save_invalid_new_name(self):
        # It is not allowed to save an environment with an already used name.
        changes = {'name': 'lxc'}
        with self.patch_create_form(changes=changes) as mock_create_form:
            self.call_view(env_name='ec2-west')
            self.assertTrue(mock_create_form.called)
            # The "save" button is the first one.
            save_button = self.get_control_buttons()[0]
            cli_helpers.emit(save_button)
        # In case of errors, the save callable is not called.
        self.assertFalse(self.save_callable.called)
        # The form has been re-rendered passing the errors.
        self.assertEqual(2, mock_create_form.call_count)
        self.assertEqual(
            {'name': 'an environment with this name already exists'},
            mock_create_form.errors)

    @mock.patch('quickstart.cli.views.env_index')
    def test_creation_view_cancel_button(self, mock_env_index):
        # The index view is called if the "cancel" button is clicked while
        # creating a new environment.
        self.call_view(env_type='ec2')
        # The "cancel" button is the second one.
        cancel_button = self.get_control_buttons()[1]
        cli_helpers.emit(cancel_button)
        mock_env_index.assert_called_once_with(self.app, self.params)

    @mock.patch('quickstart.cli.views.env_detail')
    def test_modification_view_cancel_button(self, mock_env_detail):
        # The index view is called if the "cancel" button is clicked while
        # creating a new environment.
        self.call_view(env_name='ec2-west')
        # The "cancel" button is the second one.
        cancel_button = self.get_control_buttons()[1]
        cli_helpers.emit(cancel_button)
        mock_env_detail.assert_called_once_with(
            self.app, self.params, self.env_data)
