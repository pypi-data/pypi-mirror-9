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

"""Juju Quickstart utilities for communicating with the Juju charm store."""

from __future__ import unicode_literals

import json

from quickstart import (
    netutils,
    serializers,
    settings,
)


class NotFoundError(Exception):
    """Represent a not found HTTP error while communicating with the store."""


def get(path):
    """Send a GET request to the charm store at the given path.

    The path must not include the charm store API version identifier. In
    essence, the path must exclude the "/v4/" fragment.

    Return the string content returned by the charm store.
    Raise a NotFoundError if a 404 not found response is returned.
    Raise an IOError if any other problems occur while communicating with the
    charm store.
    """
    url = settings.CHARMSTORE_API + path.lstrip('/')
    try:
        return netutils.urlread(url)
    except netutils.NotFoundError as err:
        msg = b'charm store resource not found at {}: {}'.format(
            url.encode('utf-8'), err)
        raise NotFoundError(msg)
    except IOError as err:
        msg = b'cannot communicate with the charm store at {}: {}'.format(
            url.encode('utf-8'), err)
        raise IOError(msg)


def get_reference(reference, path):
    """Retrieve the charm store contents for the given reference and path.

    The reference argument identifies a charm or bundle entity and must be an
    instance of "quickstart.models.references.Reference".

    For instance, to retrieve the hash of a charm reference, use the following:

        hash = get_reference(reference, '/meta/hash')

    Raise a NotFoundError if an entity with the given reference cannot be
    found in the charm store.
    Raise an IOError if any other problems occur while communicating with the
    charm store.
    """
    if not path.startswith('/'):
        path = '/' + path
    return get(reference.path() + path)


def resolve(name, series=None):
    """Return the fully qualified id of the entity with the given name.

    If the optional series is provided, resolve the entity of the given series.

    Raise a NotFoundError if an entity with the given name and optional series
    cannot be found in the charm store.
    Raise an IOError if any other problems occur while communicating with the
    charm store.
    Raise a ValueError if the API returns invalid data.
    """
    series_part = '' if series is None else '{}/'.format(series)
    content = get(series_part + name + '/meta/id')
    data = json.loads(content)
    entity_id = data.get('Id')
    if entity_id is None:
        msg = 'unable to resolve entity id {}{}'.format(series_part, name)
        raise ValueError(msg.encode('utf-8'))
    return entity_id


def get_bundle_data(reference):
    """Retrieve and return the bundle data for the given bundle reference.

    The bundle data is returned as a YAML decoded value.
    The reference argument identifies a bundle entity and must be an instance
    of "quickstart.models.references.Reference".

    Raise a ValueError if the returned content is not a valid YAML, or if the
    given reference does not represent a bundle.
    Raise a NotFoundError if a bundle with the given reference cannot be found
    in the charm store.
    Raise an IOError if any other problems occur while communicating with the
    charm store.
    """
    return _retrieve_and_parse_bundle_data(reference, '/archive/bundle.yaml')


def get_legacy_bundle_data(reference):
    """Retrieve and return the bundle legacy data for the given reference.

    The bundle data is returned as a YAML decoded value and represents the
    legacy bundle with a top level bundle name node.
    The reference argument identifies a bundle entity and must be an instance
    of "quickstart.models.references.Reference".

    Raise a ValueError if the returned content is not a valid YAML, or if the
    given reference does not represent a bundle.
    Raise a NotFoundError if a bundle with the given reference cannot be found
    in the charm store.
    Raise an IOError if any other problems occur while communicating with the
    charm store.
    """
    return _retrieve_and_parse_bundle_data(
        reference, '/archive/bundles.yaml.orig')


def _retrieve_and_parse_bundle_data(reference, path):
    """Retrieve and parse the bundle YAML for the given reference and path.

    Raise a ValueError if the returned content is not a valid YAML, or if the
    given reference does not represent a bundle.
    Raise a NotFoundError if a bundle with the given reference cannot be found
    in the charm store.
    Raise an IOError if any other problems occur while communicating with the
    charm store.
    """
    if not reference.is_bundle():
        raise ValueError(
            b'expected a bundle, provided charm {}'.format(reference))
    content = get_reference(reference, path)
    return load_bundle_yaml(content)


def load_bundle_yaml(content):
    """Deserialize the given YAML encoded bundle content.

    Raise a ValueError if the content is not valid.
    """
    try:
        return serializers.yaml_load(content)
    except Exception as err:
        msg = b'unable to parse the bundle content: {}'.format(err)
        raise ValueError(msg)
