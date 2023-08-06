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

"""Juju Quickstart distribution file."""

from __future__ import print_function

import ConfigParser
from distutils.core import Command
from distutils.version import StrictVersion
import os
import shlex
import sys

from setuptools import (
    find_packages,
    setup,
)
from setuptools.command.test import test as TestCommand


ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_NAME = 'quickstart'

os.chdir(ROOT)
project = __import__(PROJECT_NAME)


def get_package_data():
    """Return Juju Quickstart package data by walking through the project.

    The package data includes all non-python files that must be included in
    the source distribution.
    """
    data_files = []
    for dirpath, dirnames, filenames in os.walk(PROJECT_NAME):
        for i, dirname in enumerate(dirnames):
            if dirname.startswith('.'):
                del dirnames[i]
        if '__init__.py' in filenames:
            continue
        elif filenames:
            for f in filenames:
                data_files.append(os.path.join(
                    dirpath[len(PROJECT_NAME) + 1:], f))
    return {PROJECT_NAME: data_files}


def get_long_description():
    """Retrieve the project long description from the README.rst file."""
    with open(os.path.join(ROOT, 'README.rst')) as readme_file:
        return readme_file.read()


def get_install_requires():
    """Dynamically generate the requirements list by parsing the tox file."""
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(ROOT, 'tox.ini'))
    all_versions = {}
    test_requirements = '{[testenv]deps}'
    platforms = config.get('tox', 'envlist').split(',')
    for platform in platforms:
        section = 'testenv:{}'.format(platform)
        deps = filter(None, config.get(section, 'deps').splitlines())
        for requirement in deps:
            requirement = requirement.strip()
            if requirement.startswith('#') or requirement == test_requirements:
                continue
            name, version = requirement.split('==')
            versions = all_versions.setdefault(name, set())
            versions.add(version)
    requirements = []
    for name, versions in all_versions.items():
        if len(versions) == 1:
            requirements.append('{}=={}'.format(name, versions.pop()))
            continue
        versions = list(sorted(versions, key=StrictVersion))
        requirements.append(
            '{}>={},<={}'.format(name, versions[0], versions[-1]))
    return requirements


class RequirementsCommand(Command):
    """Set up the requirements command."""

    description = 'output program requirements'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        requirements = get_install_requires()
        print('\n{}'.format('\n'.join(requirements)))


class ToxCommand(TestCommand):
    """Set up the tox testing command."""

    user_options = [('tox-args=', 'a', 'Arguments to pass to tox')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Import here, cause outside the eggs aren't loaded.
        import tox
        args = [] if self.tox_args is None else shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


setup(
    name='juju-quickstart',
    version=project.get_version(),
    description=project.__doc__,
    long_description=get_long_description(),
    author='The Juju GUI team',
    author_email='juju-gui@lists.ubuntu.com',
    url='https://launchpad.net/juju-quickstart',
    keywords='juju quickstart plugin',
    packages=find_packages(),
    package_data=get_package_data(),
    scripts=['juju-quickstart'],
    install_requires=get_install_requires(),
    tests_require=['tox'],
    cmdclass = {
        'requirements': RequirementsCommand,
        'test': ToxCommand,
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: System :: Installation/Setup',
    ],
)
