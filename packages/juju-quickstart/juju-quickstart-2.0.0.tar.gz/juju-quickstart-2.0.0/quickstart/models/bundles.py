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

"""Juju Quickstart bundles management.

This module defines objects and functions that help working with bundles.
Bundles are described by a YAML content defining a collection of services in a
Juju topology, along with their options, relations and unit placement.

Published bundles are identified by a charm store id and by the corresponding
URL in jujucharms.com, just like regular charms. The reference object in
"quickstart.models.references.Reference" can be used to identify a bundle.

In this module, the Bundle class represents a bundle that may or may not have
a specific reference id. For instance, a reference is not set on a bundle if
its contents are retrieved from an arbitrary local or remote location.

Juju Quickstart usually instantiates bundles using the "from_source" helper
below, which retrieves the bundle content from all the supported sources,
validates it and then creates a "Bundle" instance with the validated content
and the bundle reference if avaliable.

Use "parse_yaml" to parse and validate a YAML encoded string as a bundle
content. If the YAML decoded object is already available, the same validation
can be achieved using the "validate" function directly.
"""

from __future__ import unicode_literals

import codecs
import collections
import logging
import os

from quickstart import (
    netutils,
    serializers,
    settings,
)
from quickstart.models import references


class Bundle(object):
    """Store information about a charm store bundle entity"""

    def __init__(self, data, reference=None):
        """Initialize the bundle.

        The data argument is the bundle YAML decoded content.
        An optional entity reference can be provided as an instance of
        "quickstart.models.references.Reference".
        """
        self.data = data
        self.reference = reference

    def __str__(self):
        """Return the byte string representation of this bundle."""
        return self.__unicode__().encode('utf-8')

    def __unicode__(self):
        """Return the unicode string representation of this bundle."""
        parts = ['bundle']
        if self.reference is not None:
            parts.append(self.reference.jujucharms_id())
        return ' '.join(parts)

    def __repr__(self):
        return b'<Bundle: {}>'.format(bytes(self))

    def serialize(self):
        """Serialize the bundle data as a YAML encoded string."""
        return serializers.yaml_dump(self.data)

    def serialize_legacy(self):
        """Serialize the bundle data as a YAML encoded string.

        The resulting string uses the legacy API version 3 format.
        """
        return serializers.yaml_dump({'bundle': self.data})

    def services(self):
        """Return a list of service names included in the bundle.

        Service names are returned in alphabetical order.
        """
        return sorted(self.data['services'].keys())


def from_source(source, name=None):
    """Return a bundle YAML encoded string and id from the given source.

    The source argument is a string, and can be provided as:

        - a bundle path as shown in jujucharms.com, e.g. "mediawiki-single" or
          "u/bigdata-dev/apache-analytics-sql";

        - a bundle path as shown in jujucharms.com including the bundle
          revision, e.g. "mediawiki-single/7" or "u/frankban/django/42";

        - the two forms above with leading or trailing slashes, e.g.
          "/mediawiki-scalable" or "/u/frankban/django/42";

        - a full jujucharms.com URL, e.g. "https://jujucharms.com/django/" or
          "https://jujucharms.com/u/bigdata-dev/apache-analytics-sql";

        - a full jujucharms.com URL including the bundle revision, e.g.
          "https://jujucharms.com/django/2/";

        - a URL ("http:" or "https:") to a YAML/JSON, e.g.
          "https://raw.github.com/user/my/master/bundles.yaml";

        - a local path to a YAML/JSON file, ending with ".yaml" or ".json",
          e.g. "mybundle.yaml" or "~/bundles/django.json";

        - an old style bundle fully qualified URL, e.g.
          "bundle:~myuser/mediawiki/42/single";

        - and old style bundle URL without user and/or revision, e.g.
          "bundle:mediawiki/single" or "bundle:~user/mediawiki/single".

    Return a Bundle instance whose bundle reference attribute is None if this
    information cannot be inferred from the given source.

    Raise a ValueError if the given source is not valid.
    Raise an IOError if the YAML content cannot be retrieved from the given
    local or remote source.
    """
    if source.startswith('bundle:'):
        # The source refers to an old style bundle URL.
        reference = references.Reference.from_charmworld_url(source)
        logging.warn(
            'this bundle URL is deprecated: please use the new format: '
            '{}'.format(reference.jujucharms_id()))
        return _bundle_from_reference(reference)

    has_extension = source.endswith('.yaml') or source.endswith('.json')
    is_remote = source.startswith('http://') or source.startswith('https://')
    if has_extension and not is_remote:
        # The source refers to a local file.
        data = _parse_and_flatten_yaml(_retrieve_from_file(source), name)
        return Bundle(data)

    try:
        reference = references.Reference.from_jujucharms_url(source)
    except ValueError:
        if is_remote:
            # The source is an arbitrary URL to a YAML/JSON content.
            data = _parse_and_flatten_yaml(_retrieve_from_url(source), name)
            return Bundle(data)
        # No other options are available.
        raise

    if not reference.is_bundle():
        raise ValueError(
            b'expected a bundle, provided charm {}'.format(reference))

    # The source refers to a bundle URL in jujucharms.com.
    return _bundle_from_reference(reference)


def _bundle_from_reference(reference):
    """Retrieve bundle YAML contents from its reference in the charm store.

    The path of an entity in the charm store is the fully qualified URL without
    the schema. The schema is implicitly set to "cs" (charm store entity), e.g.
    "vivid/django" or "~who/trusty/mediawiki-42".

    Return a Bundle instance which includes the retrieved data and the given
    reference.
    Raise a IOError if a problem is encountered while fetching the YAML
    content from the charm store.
    Raise a ValueError if the bundle content is not valid.
    """
    url = settings.CHARMSTORE_API + reference.path() + '/archive/bundle.yaml'
    content = _retrieve_from_url(url)
    data = parse_yaml(content)
    return Bundle(data, reference=reference)


def _retrieve_from_url(url):
    """Retrieve bundle YAML content from the given URL.

    Return the bundle content as a YAML encoded string.
    Raise a IOError if a problem is encountered while opening the URL.
    """
    try:
        return netutils.urlread(url)
    except IOError as err:
        msg = b'cannot retrieve bundle from remote URL {}: {}'.format(
            url.encode('utf-8'), err)
        raise IOError(msg)


def _retrieve_from_file(path):
    """Retrieve bundle YAML content from the given local file path.

    Return the bundle content as a YAML encoded string.
    Raise a IOError if a problem is encountered while opening the file.
    """
    path = os.path.abspath(os.path.expanduser(path))
    try:
        return codecs.open(path.encode('utf-8'), encoding='utf-8').read()
    except IOError as err:
        raise IOError(
            b'cannot retrieve bundle from local file: {}'.format(err))


def parse_yaml(content):
    """Parse and validate the given bundle content as a YAML encoded string.

    Note that the bundle validation performed by Juju Quickstart is weak by
    design: it just checks that the content looks like a bundle YAML. Contents
    provided by the charm store are already known as valid. For other sources,
    a more cogent validation is done down in the stack, when the content is
    sent to the GUI server and then to the Juju deployer.

    Return the resulting YAML decoded dictionary.
    Raise a ValueError if:
        - the bundle YAML contents are not parsable by YAML;
        - the YAML contents are not properly structured;
        - the bundle does not include services.
    """
    data = _open_yaml(content)
    # Validate the bundle data.
    validate(data)
    return data


def _parse_and_flatten_yaml(content, name):
    """Parse and validate the given bundle content.

    The content is provided as a YAML encoded string and can be either a new
    style flat bundle or a legacy bundle format.
    In both cases, the returned YAML decoded data represents a new style
    bundle (API version 4).

    Raise a ValueError if:
        - the bundle YAML contents are not parsable by YAML;
        - the YAML contents are not properly structured;
        - the bundle name is specified but not included in the bundle file;
        - the bundle name is not specified and the bundle file includes more
          than one bundle;
        - the bundle does not include services.
    """
    data = _open_yaml(content)
    services = data.get('services')
    # The internal structure of a bundle in the API version 4 does not include
    # a wrapping namespace with the bundle name. That's why the check below,
    # despite its ugliness, is quite effective.
    if services and 'services' not in services:
        # This is an API version 4 bundle.
        validate(data)
        return data
    num_bundles = len(data)
    if not num_bundles:
        raise ValueError(b'no bundles found in the provided list of bundles')
    names = ', '.join(sorted(data.keys()))
    if name is None:
        if num_bundles > 1:
            msg = 'multiple bundles found ({}) but no bundle name specified'
            raise ValueError(msg.format(names).encode('utf-8'))
        data = data.values()[0]
    else:
        data = data.get(name)
        if data is None:
            msg = 'bundle {} not found in the provided list of bundles ({})'
            raise ValueError(msg.format(name, names).encode('utf-8'))
    validate(data)
    return data


def _open_yaml(content):
    """Deserialize the given content, that must be a YAML encoded dictionary.

    Raise a ValueError if the content is not valid.
    """
    try:
        data = serializers.yaml_load(content)
    except Exception as err:
        msg = b'unable to parse the bundle content: {}'.format(err)
        raise ValueError(msg)
    # Ensure the bundle content is well formed.
    if not isinstance(data, collections.Mapping):
        msg = 'invalid YAML content: {}'.format(data)
        raise ValueError(msg.encode('utf-8'))
    return data


def validate(data):
    """Validate the given YAML decoded bundle data.

    Note that the bundle validation performed by Juju Quickstart is weak by
    design: it just checks that the content looks like a bundle YAML. Contents
    provided by the charm store are already known as valid. For other sources,
    a more cogent validation is done down in the stack, when the content is
    sent to the GUI server and then to the Juju deployer.

    Raise a ValueError if:
        - the YAML contents are not properly structured;
        - the bundle does not include services.
    """
    # Retrieve the bundle services.
    try:
        services = data['services'].keys()
    except (AttributeError, KeyError, TypeError):
        content = serializers.yaml_dump(data).strip()
        msg = 'unable to retrieve bundle services: {}'.format(content)
        raise ValueError(msg.encode('utf-8'))
    # Ensure at least one service is defined in the bundle.
    if not services:
        raise ValueError(b'no services found in the bundle')
    # Check that the Juju GUI charm is not included as a service.
    if settings.JUJU_GUI_SERVICE_NAME in services:
        raise ValueError(
            b'the provided bundle contains an instance of juju-gui. Juju '
            b'Quickstart will install the latest version of the Juju GUI '
            b'automatically; please remove juju-gui from the bundle')
