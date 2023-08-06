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

"""Juju Quickstart CLI application views.

This module contains the Quickstart view implementations along with a function
(show) to easily start a view automatically creating an Urwid application.

To start a Quickstart interactive session, just run the following:

    show(view, *args)

The code above sets up a Quickstart branded CLI application, then calls the
given view callable passing the application object ready to be configured
and all the given optional arguments. Finally the interactive session is
started, and the show function blocks until the user or the view itself
request to exit the application.

A view is a callable receiving an App object (a named tuple of functions) and
other optional arguments (based on specific view needs). A view function can
configure the Urwid application using the API exposed by the application object
(see quickstart.cli.base.setup_urwid_app).

Assume a view is defined like the following:

    def myview(app, title):
        app.set_title(title)
        app.set_return_value_on_exit(42)

The view above, requiring a title argument, can be started this way:

    show(myview, 'this title will be shown in the header')

At this point the application main loop is started, and the user can interact
with the CLI interface. There are two ways to stop the interactive session:
    1) the user explicitly requests to exit. The Urwid application is
       automatically configured to allow the user to quit whenever she wants by
       pressing a keyboard shortcut;
    2) a view decides it is time to quit (e.g. reacting to an event/input).

In both cases, the show function returns something to the caller:
    1) when the user explicitly requests to quit, None is returned by default.
       However, the view can change this default value by calling
       app.set_return_value_on_exit(some value). For instance, the
       show(myview...) call above would return 42. It is safe to call the
       set_return_value_on_exit API multiple times in order to overwrite the
       value returned on user exit;
    2) to force the end of the interactive session, a view can raise a
       quickstart.cli.ui.AppExit exception, passing a return value: if the
       application is exited this way, then show() returns the value
       encapsulated in the exception. Note that this exception can be raised
       as a reaction to an event, and not in the first execution of the view
       body, i.e. during the app configuration.

The above is better described by code:

    from quickstart.cli import views, ui

    def button_view(app):

        def exit():
            raise ui.AppExit(True)

        app.set_return_value_on_exit(False)
        app.set_title('behold the button below')
        button = ui.MenuButton('press to exit', ui.thunk(exit))
        widgets = urwid.ListBox(urwid.SimpleFocusListWalker([button]))
        app.set_contents(widgets)

    pressed = views.show(button_view)

In this example the button_view function configures the App to show a button.
Clicking that button an AppExit(True) is raised. The return value on exit
instead is set by the view itself to False. This means that "pressed" will be
True if the user exited using the button, or False if the user exited using the
global shortcut.

As a final note, it is absolutely safe for a view to call, directly or
indirectly, other views, as long as all the arguments required by the other
views, including the App object, are properly provided. This is effectively the
proposed solution to build multi-views CLI applications in Quickstart.
"""

from __future__ import (
    print_function,
    unicode_literals,
)

import copy
import functools
import operator

import urwid

from quickstart import (
    maas,
    platform_support,
    settings,
)
from quickstart.cli import (
    base,
    forms,
    ui,
)
from quickstart.models import (
    envs,
    jenv,
)


def show(view, *args):
    """Start an Urwid interactive session showing the given view.

    The view is called passing an App named tuple and the provided *args.

    Block until the main loop is stopped, either by the user with the exit
    shortcut or by the view itself. In both cases, an ui.AppExit is raised, and
    the return value is encapsulated in the exception.
    """
    loop, app = base.setup_urwid_app()
    try:
        # Execute the view.
        view(app, *args)
        # Start the Urwid interactive session (main loop).
        loop.run()
    except ui.AppExit as err:
        # The print below ensures the screen is properly refreshed when
        # exiting the interactive session.
        print('interactive session closed')
        return err.return_value


def _save_and_exit(env_db, env_data, save_callable):
    """Add the new environment env_data to the env_db.

    Exit the interactive session passing the newly saved environment, so that
    it is bootstrapped by the application.
    """
    envs.set_env_data(env_db, None, env_data)
    save_callable(env_db)
    # Use the newly created environment.
    raise ui.AppExit((env_db, env_data))


def env_index(app, params):
    """Show the Juju environments list.

    The env_detail view is displayed when the user clicks on an environment.
    From here it is also possible to switch to the edit view in order to create
    a new environment.

    Receives a params namedtuple-like object including the following fields:
        - env_type_db: the environments meta information;
        - env_db: the environments database;
        - jenv_db: the jenv files database;
        - save_callable: a function called to save a new environment database.
    See quickstart.cli.params.Params.
    """
    # XXX frankban 16/12/2014: this function is too long, subdivide it.
    params = params.copy()
    # All the environment views return a tuple (new_env_db, env_data).
    # Set the env_data to None in the case the user quits the application
    # without selecting an environment to use.
    app.set_return_value_on_exit((params.env_db, None))
    detail_view = functools.partial(env_detail, app, params)
    jenv_view = functools.partial(jenv_detail, app, params)
    edit_view = functools.partial(env_edit, app, params)
    # Alphabetically sort the existing environments.
    environments = sorted([
        envs.get_env_data(params.env_db, env_name)
        for env_name in params.env_db['environments']
    ], key=operator.itemgetter('name'))

    platform = platform_support.get_platform()
    supports_local = platform_support.supports_local(platform)

    if environments:
        title = 'Select an existing Juju environment or create a new one'
        widgets = [
            urwid.Text(('highlight', 'Manage existing environments:')),
            urwid.Divider(),
        ]
    else:
        title = 'No Juju environments already set up: please create one'
        widgets = [
            urwid.Text([
                ('highlight', 'Welcome to Juju Quickstart!'),
                '\nYou can use this interactive session to manage your Juju '
                'environments.\nInteractive mode has been automatically '
                'started because no environments have been found. After '
                'creating your first environment you can start Juju '
                'Quickstart in interactive mode again by passing the -i flag, '
                'e.g.:\n',
                ('highlight', '$ juju quickstart -i'),
            ]),
        ]
        # If the MAAS CLI is available and it is logged in to a remote API,
        # offer to automatically create and bootstrap a MAAS environment with
        # the info retrieved by calling the MAAS CLI.
        if maas.cli_available():
            maas_api_data = maas.get_api_info()
            if maas_api_data is not None:
                maas_name, maas_server, maas_api_key = maas_api_data
                maas_callback = ui.thunk(
                    _create_and_start_maas_env,
                    params.env_type_db, params.env_db, params.save_callable,
                    maas_name, maas_server, maas_api_key)
                widgets.extend([
                    urwid.Text([
                        '\nThe ',
                        ('highlight', maas_name),
                        ' MAAS (bare metal) remote API at ',
                        ('highlight', maas_server),
                        ' has been detected, and can be used to '
                        'automatically set up a MAAS environment. '
                        'To do that, just click the link below:',
                    ]),
                    urwid.Divider(),
                    ui.MenuButton(
                        '\N{BULLET} automatically create and bootstrap the {} '
                        'MAAS environment'.format(maas_name), maas_callback),
                ])

        # If the current platform supports local Juju environments, add an
        # option to automatically create and bootstrap one.
        if supports_local:
            local_callback = ui.thunk(
                _create_and_start_local_env,
                params.env_type_db, params.env_db, params.save_callable)
            widgets.extend([
                urwid.Text([
                    '\nAt the bottom of the page you can find links to '
                    'manually create new environments. If you instead prefer '
                    'to quickly start your Juju experience in a local '
                    'environment (LXC), just click the link below:',
                ]),
                urwid.Divider(),
                ui.MenuButton(
                    '\N{BULLET} automatically create and bootstrap a local '
                    'environment', local_callback),
            ])

    app.set_title(title)
    # Start creating the page contents: a list of selectable environments.
    # Wouldn't it be nice if we were able to highlight in some way the
    # currently running environments? Unfortunately this requires calling
    # "juju status" for each environment in the list, which is expensive and
    # time consuming.
    focus_position = None
    active_found = default_found = errors_found = False
    existing_widgets_num = len(widgets)
    remaining_jenv_db = copy.deepcopy(params.jenv_db)
    for position, env_data in enumerate(environments):
        bullet = '\N{BULLET}'
        # Is this environment the default one?
        if env_data['is-default']:
            default_found = True
            # The first two positions are the section header and the divider.
            focus_position = position + existing_widgets_num
            bullet = '\N{CHECK MARK}'
        if remaining_jenv_db['environments'].pop(env_data['name'], None):
            # This is an active environment. Is it running? Who knows...
            active_found = True
            bullet = ('active', bullet)
        else:
            # Check if this environment is valid.
            env_metadata = envs.get_env_metadata(params.env_type_db, env_data)
            errors = envs.validate(env_metadata, env_data)
            if errors:
                errors_found = True
                bullet = ('error', bullet)
        # Create a label for the environment.
        env_short_description = envs.get_env_short_description(env_data)
        text = [bullet, ' {}'.format(env_short_description)]
        widgets.append(ui.MenuButton(text, ui.thunk(detail_view, env_data)))

    # Alphabetically sort the remaining environments not included in the
    # environments.yaml file.
    environments = list(sorted([
        envs.get_env_data(remaining_jenv_db, env_name)
        for env_name in remaining_jenv_db['environments']
    ], key=operator.itemgetter('name')))

    if environments:
        # List the remaining active environments. Those environments are not
        # included in the environments.yaml file: they are probably imported
        # and assumed to be working/active. The user has the ability to select
        # them.
        widgets.extend([
            urwid.Divider(),
            urwid.Text(('highlight', 'Other active environments')),
            urwid.Text(
                '(imported/not included in your environments.yaml file):'),
            urwid.Divider(),
        ])
        bullet = ('active', '\N{BULLET}')
        for env_data in environments:
            env_short_description = jenv.get_env_short_description(env_data)
            text = [bullet, ' {}'.format(env_short_description)]
            widgets.append(ui.MenuButton(text, ui.thunk(jenv_view, env_data)))

    # Set up the "create a new environment" section.
    widgets.extend([
        urwid.Divider(),
        urwid.Text(('highlight', 'Create a new environment:')),
        urwid.Divider(),
    ])
    # The Juju GUI can be safely installed in the bootstrap node only if its
    # series matches one of the series supported by the GUI.
    # Suggest the most recent supported series by pre-filling the value.
    preferred_series = settings.JUJU_GUI_SUPPORTED_SERIES[-1]
    # Retrieve the list of supported environment types: exclude the local
    # environment if not supported by the current OS platform.
    filter_function = None
    if not supports_local:
        filter_function = lambda env_type, _: env_type != 'local'
    supported_env_types = envs.get_supported_env_types(
        params.env_type_db, filter_function=filter_function)
    # Add the buttons used to create new environments.
    widgets.extend([
        ui.MenuButton(
            ['\N{BULLET} new ', ('highlight', label), ' environment'],
            ui.thunk(edit_view, {
                'type': env_type, 'default-series': preferred_series})
        )
        for env_type, label in supported_env_types
    ])

    # Set up the application status messages.
    status = [' \N{UPWARDS ARROW LEFTWARDS OF DOWNWARDS ARROW} navigate ']
    if default_found:
        status.append(' \N{CHECK MARK} default ')
    if active_found:
        status.extend([('active status', ' \N{BULLET}'), ' active '])
    if errors_found:
        status.extend([('error status', ' \N{BULLET}'), ' has errors '])
    app.set_status(status)
    # Set up the application contents.
    contents = urwid.ListBox(urwid.SimpleFocusListWalker(widgets))
    if focus_position is not None:
        contents.set_focus(focus_position)
    app.set_contents(contents)


def _create_and_start_local_env(env_type_db, env_db, save_callable):
    """Automatically create and use a local environment named "local".

    This function can only be called when there are no environments in the
    database. For this reason, the new environment is set as default.
    Exit the interactive session selecting the newly created environment.
    """
    env_data = envs.create_local_env_data(
        env_type_db, 'local', is_default=True)
    _save_and_exit(env_db, env_data, save_callable)


def _create_and_start_maas_env(
        env_type_db, env_db, save_callable, name, server, api_key):
    """Automatically create and use a MAAS environment.

    This function can only be called when there are no environments in the
    database. For this reason, the new environment is set as default.
    Exit the interactive session selecting the newly created environment.
    """
    env_data = envs.create_maas_env_data(
        env_type_db, name, server, api_key, is_default=True)
    _save_and_exit(env_db, env_data, save_callable)


def env_detail(app, params, env_data):
    """Show details on a Juju environment.

    From this view it is possible to start the environment, set it as default,
    edit/remove the environment.

    Receives a params namedtuple-like object including the following fields:
        - env_type_db: the environments meta information;
        - env_db: the environments database;
        - jenv_db: the jenv files database;
        - save_callable: a function called to save a new environment database.
    See quickstart.cli.params.Params.
    Also receives the current environment data env_data.
    """
    params = params.copy()
    # All the environment views return a tuple (new_env_db, env_data).
    # Set the env_data to None in the case the user quits the application
    # without selecting an environment to use.
    app.set_return_value_on_exit((params.env_db, None))
    index_view = functools.partial(env_index, app, params)
    edit_view = functools.partial(env_edit, app, params, env_data)

    env_metadata = envs.get_env_metadata(params.env_type_db, env_data)
    app.set_title(envs.get_env_short_description(env_data))
    # Validate the environment.
    errors = envs.validate(env_metadata, env_data)
    widgets = []
    field_value_pairs = envs.map_fields_to_env_data(env_metadata, env_data)
    for field, value in field_value_pairs:
        if field.required or (value is not None):
            label = '{}: '.format(field.name)
            if field.name in errors:
                label = ('error', label)
            text = [label, ('highlight', field.display(value))]
            widgets.append(urwid.Text(text))
    controls = [ui.MenuButton('back', ui.thunk(index_view))]
    status = [' \N{RIGHTWARDS ARROW OVER LEFTWARDS ARROW} navigate ']
    if errors:
        status.extend([
            ('error status', ' \N{LOWER SEVEN EIGHTHS BLOCK}'),
            ' field error ',
        ])
    else:
        # Without errors, it is possible to use/start this environment.
        use_callback = ui.thunk(_use, params.env_db, env_data)
        controls.append(ui.MenuButton('use', use_callback))
    app.set_status(status)
    if not env_data['is-default']:
        # If the environment is not the default one, it is possible to set it
        # as default.
        set_default_callback = ui.thunk(
            _set_default, params.env_db, env_data, params.save_callable,
            app.set_message, index_view)
        controls.append(ui.MenuButton('set default', set_default_callback))
    # Add the controls to edit and remove the environment.
    remove_callback = ui.thunk(
        _remove, params.env_db, env_data, params.save_callable,
        app.set_message, index_view)
    confirm_removal_callback = ui.thunk(
        _confirm_removal, app, env_data, remove_callback)
    controls.extend([
        ui.MenuButton('edit', ui.thunk(edit_view)),
        ui.MenuButton(('control alert', 'remove'), confirm_removal_callback),
    ])
    widgets.append(ui.create_controls(*controls))
    listbox = urwid.ListBox(urwid.SimpleFocusListWalker(widgets))
    app.set_contents(listbox)


def _use(env_db, env_data):
    """Use the selected environment.

    Quit the interactive session returning the (possibly modified)
    environment database and the environment data corresponding to the
    selected environment.
    """
    raise ui.AppExit((env_db, env_data))


def _set_default(env_db, env_data, save_callable, set_message, redirect_view):
    """Set this environment as the default one.

    Save the env_db and return to the given view.
    Also output a notification using the given set_message callable.
    """
    env_name = env_data['name']
    env_db['default'] = env_name
    save_callable(env_db)
    set_message('{} successfully set as default'.format(env_name))
    redirect_view()


def _confirm_removal(app, env_data, remove_callable):
    """Ask confirmation before removing an environment."""
    ui.show_dialog(
        app, 'Remove the {} environment'.format(env_data['name']),
        'This action cannot be undone!',
        actions=[(('control alert', 'confirm'), remove_callable)],
    )


def _remove(env_db, env_data, save_callable, set_message, redirect_view):
    """Remove the environment represented by env_data from the database.

    Save the new env_db and return to the given view.
    Also output a notification using the given set_message callable.
    """
    env_name = env_data['name']
    envs.remove_env(env_db, env_name)
    save_callable(env_db)
    set_message('{} successfully removed'.format(env_name))
    redirect_view()


def jenv_detail(app, params, env_data):
    """Show details on a Juju imported environment.

    The environment is not included in the environments.yaml file, but just
    found in the jenv database.
    From this view it is possible to start the environment.

    Receives a params namedtuple-like object including the following fields:
        - env_type_db: the environments meta information;
        - env_db: the environments database;
        - jenv_db: the jenv files database;
        - save_callable: a function called to save a new environment database;
    See quickstart.cli.params.Params.
    Also receives the current environment data env_data.
    """
    params = params.copy()
    # All the environment views return a tuple (new_env_db, env_data).
    # Set the env_data to None in the case the user quits the application
    # without selecting an environment to use.
    app.set_return_value_on_exit((params.env_db, None))
    index_view = functools.partial(env_index, app, params)

    app.set_title(jenv.get_env_short_description(env_data))
    widgets = []
    for key, value in jenv.get_env_details(env_data):
        widgets.append(urwid.Text(['{}: '.format(key), ('highlight', value)]))
    widgets.extend([
        urwid.Divider(),
        urwid.Text([
            ('highlight', 'Imported active environment.\n'),
            'This environment is not included in your environments.yaml file.'
            '\nFor this reason, it is not possible to edit it.\n'
            'However, you can use the link below to ',
            ('highlight', 'use Juju Quickstart'),
            ' with this environment or ',
            ('highlight', 'remove the corresponding jenv file'),
            '.\n'
            'Note that removing the Juju generated environment file does not '
            'destroy the corresponding active environment.'
        ]),
    ])

    remove_callback = ui.thunk(
        _remove_jenv, params.jenv_db, env_data, params.remove_jenv_callable,
        app.set_message, index_view)
    confirm_removal_callback = ui.thunk(
        _confirm_removal, app, env_data, remove_callback)
    controls = [
        ui.MenuButton('back', ui.thunk(index_view)),
        ui.MenuButton('use', ui.thunk(_use, params.env_db, env_data)),
        ui.MenuButton(('control alert', 'remove'), confirm_removal_callback),
    ]
    widgets.append(ui.create_controls(*controls))
    listbox = urwid.ListBox(urwid.SimpleFocusListWalker(widgets))
    app.set_contents(listbox)
    app.set_status([' \N{RIGHTWARDS ARROW OVER LEFTWARDS ARROW} navigate '])


def _remove_jenv(
        jenv_db, env_data, remove_jenv_callable, set_message, redirect_view):
    """Remove the jenv file corresonding to the env_data environment.

    Update the provided jenv_db and return to the given view.
    Also output a notification using the given set_message callable.
    """
    env_name = env_data['name']
    # Remove the jenv file.
    msg = remove_jenv_callable(env_name)
    if msg is None:
        msg = '{} successfully removed'.format(env_name)
        # Also remove the environments from the jenv database.
        del jenv_db['environments'][env_name]
    set_message(msg)
    redirect_view()


def env_edit(app, params, env_data):
    """Create or modify a Juju environment.

    This view displays an edit form allowing for environment
    creation/modification. Saving the form redirects to the environment detail
    view if the values are valid.

    Receives a params namedtuple-like object including the following fields:
        - env_type_db: the environments meta information;
        - env_db: the environments database;
        - jenv_db: the jenv files database;
        - save_callable: a function called to save a new environment database;
    See quickstart.cli.params.Params.
    Also receives the current environment data env_data.

    The last value (env_data) indicates whether this view is used to create a
    new environment or to change an existing one. In the former case, env_data
    does not include the "name" key. If instead the environment already exists,
    env_data includes the "name" key and all the other environment info.
    """
    params = params.copy()
    # All the environment views return a tuple (new_env_db, env_data).
    # Set the env_data to None in the case the user quits the application
    # without selecting an environment to use.
    app.set_return_value_on_exit((params.env_db, None))
    env_metadata = envs.get_env_metadata(params.env_type_db, env_data)
    index_view = functools.partial(env_index, app, params)
    detail_view = functools.partial(env_detail, app, params)
    if 'name' in env_data:
        exists = True
        title = 'Edit the {} environment'
        # Retrieve all the errors for the existing environment.
        initial_errors = envs.validate(env_metadata, env_data)
    else:
        exists = False
        title = 'Create a new {} environment'
        # The environment does not exist: avoid bothering the user with errors
        # before the form is submitted.
        initial_errors = {}
    app.set_title(title.format(env_data['type']))
    app.set_status([
        ' \N{UPWARDS ARROW LEFTWARDS OF DOWNWARDS ARROW}'
        ' \N{LEFTWARDS ARROW TO BAR OVER RIGHTWARDS ARROW TO BAR}'
        ' navigate ',
        ('optional status', ' \N{LOWER SEVEN EIGHTHS BLOCK}'),
        ' optional field ',
        ('error status', ' \N{BULLET}'),
        ' field errors ',
    ])

    def render_form(data, errors):
        # Render the environment edit form.
        widgets = [
            urwid.Text(env_metadata['description']),
            urwid.Divider(),
        ]
        field_value_pairs = envs.map_fields_to_env_data(env_metadata, data)
        # Retrieve the form widgets and the data getter function. The latter
        # can be used to retrieve the field name/value pairs included in the
        # displayed form, including user's changes (see quickstart.cli.forms).
        form_widgets, get_new_env_data = forms.create_form(
            field_value_pairs, errors)
        widgets.extend(form_widgets)
        save_callback = ui.thunk(
            _save, params.env_db, env_data, env_metadata, params.save_callable,
            exists, get_new_env_data, render_form, app.set_message,
            detail_view)
        cancel_callback = ui.thunk(
            _cancel, env_data, exists, index_view, detail_view)
        actions = (
            ('save', save_callback),
            ('cancel', cancel_callback),
            ('restore', ui.thunk(render_form, env_data, initial_errors)),
        )
        widgets.append(forms.create_actions(actions))
        contents = ui.TabNavigationListBox(
            urwid.SimpleFocusListWalker(widgets))
        app.set_contents(contents)

    # Render the initial form.
    render_form(env_data, initial_errors)


def _save(
        env_db, env_data, env_metadata, save_callable, exists,
        get_new_env_data, render_form, set_message, redirect_view):
    """Create a new environment or save changes for an existing one.

    The new values are saved only if the new env_data is valid, in which
    case also redirect to the given view.
    """
    new_env_data = get_new_env_data()
    # Validate the new env_data.
    errors = envs.validate(env_metadata, new_env_data)
    new_name = new_env_data['name']
    initial_name = env_data.get('name')
    if (new_name != initial_name) and new_name in env_db['environments']:
        errors['name'] = 'an environment with this name already exists'
    # If errors are found, re-render the form passing the errors. This way
    # the errors are displayed as part of the form and the user is given
    # the opportunity to fix the invalid values.
    if errors:
        return render_form(new_env_data, errors)
    # Without errors, normalize the new values, update the env_db and save
    # the resulting environments database.
    env_data = envs.normalize(env_metadata, new_env_data)
    # If this is the only environment in the db, set it as the default one.
    if not env_db['environments']:
        env_data['is-default'] = True
    envs.set_env_data(env_db, initial_name, env_data)
    save_callable(env_db)
    verb = 'modified' if exists else 'created'
    set_message('{} successfully {}'.format(new_name, verb))
    return redirect_view(env_data)


def _cancel(env_data, exists, index_view, detail_view):
    """Dismiss any changes and return to the index or detail view."""
    return detail_view(env_data) if exists else index_view()
