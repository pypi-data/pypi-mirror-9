# This file is part of the Juju Quickstart Plugin, which lets users set up a
# Juju environment in very few steps (https://launchpad.net/juju-quickstart).
# Copyright (C) 2012-2013 Canonical Ltd.
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

PYTHON = python
APT_SYSDEPS = python-dev python-pip python-setuptools
# Since the python-tox package in Ubuntu uses Python 3, use pip to install tox
# instead. This also works on OSX where tox is not present in Homebrew.
PIP_SYSDEPS = tox

SYSDEPS_INSTALLED = .sysdeps-installed
DEVENV = devenv
QUICKSTART = $(DEVENV)/bin/juju-quickstart

.DEFAULT_GOAL := setup


$(QUICKSTART): juju-quickstart setup.py tox.ini
	@tox -e devenv

$(SYSDEPS_INSTALLED): Makefile
ifeq ($(shell command -v apt-get > /dev/null; echo $$?),0)
	sudo apt-get install --yes $(APT_SYSDEPS)
else
	@echo 'System dependencies can only be installed automatically on'
	@echo 'systems with "apt-get". On OSX you can manually use Homebrew'
	@echo 'if there are missing dependencies corresponding to the following'
	@echo 'Debian packages:'
	@echo '$(APT_SYSDEPS).'
endif
	sudo pip2 install $(PIP_SYSDEPS)
	touch $(SYSDEPS_INSTALLED)


.PHONY: check
check: setup
	@tox -e lint
	@tox

.PHONY: clean
clean:
	$(PYTHON) setup.py clean
	# Remove the development environments.
	rm -rfv $(DEVENV) .tox/
	# Remove distribution artifacts.
	rm -rfv *.egg build/ dist/ juju_quickstart.egg-info/ MANIFEST
	# Remove tests artifacts.
	rm -fv .coverage
	# Remove the sysdeps canary file.
	rm -fv $(SYSDEPS_INSTALLED)
	# Remove Python compiled bytecode.
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -type d -delete
	# Remove the virtualenv used in previous configurations.
	rm -rfv .venv/

.PHONY: fcheck
fcheck: setup
	$(MAKE) check JUJU_QUICKSTART_FTESTS=1

.PHONY: ftest
ftest: setup
	$(MAKE) test JUJU_QUICKSTART_FTESTS=1

.PHONY: help
help:
	@echo -e 'Juju Quickstart - list of make targets:\n'
	@echo 'make - Set up the development and testing environment.'
	@echo 'make test - Run tests.'
	@echo 'make lint - Run linter and pep8.'
	@echo 'make check - Run all the tests and lint in all supported scenarios.'
	@echo 'make ftest - Run tests (including functional tests).'
	@echo 'make fcheck - Run functional tests and lint in all scenarios.'
	@echo 'make source - Create source package.'
	@echo 'make install - Install on local system.'
	@echo 'make clean - Get rid of bytecode files, build and dist dirs, venvs.'
	@echo 'make release - Register and upload a release on PyPI.'
	@echo 'make requirements - Print out the application requirements.'
	@echo -e '\nAfter creating the development environment with "make", it is'
	@echo 'also possible to do the following:'
	@echo '- run the development version of Juju Quickstart by invoking'
	@echo '  "$(QUICKSTART)";'
	@echo '- run a specific subset of the test suite, e.g. with'
	@echo '  "$(DEVENV)/bin/nosetests quickstart/tests/test_app.py:TestWatch";'
	@echo '- use tox as usual on this project;'
	@echo '  see https://tox.readthedocs.org/en/latest/'

.PHONY: install
install:
	$(PYTHON) setup.py install
	rm -rfv ./build ./dist ./juju_quickstart.egg-info

.PHONY: lint
lint: setup
	@$(DEVENV)/bin/flake8 --ignore E731 --show-source quickstart

.PHONY: release
release: check
	$(PYTHON) setup.py register sdist upload

.PHONY: requirements
requirements:
	$(PYTHON) setup.py requirements

.PHONY: setup
setup: $(SYSDEPS_INSTALLED) $(QUICKSTART)

.PHONY: source
source:
	$(PYTHON) setup.py sdist

.PHONY: sysdeps
sysdeps: $(SYSDEPS_INSTALLED)

.PHONY: test
test: setup
	@$(DEVENV)/bin/nosetests \
		--with-coverage --cover-erase --cover-package quickstart
