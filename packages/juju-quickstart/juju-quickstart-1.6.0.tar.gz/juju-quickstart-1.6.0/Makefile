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
SYSDEPS = build-essential python-dev python-pip python-virtualenv

VENV = .venv
VENV_ACTIVATE = $(VENV)/bin/activate


$(VENV_ACTIVATE): test-requirements.pip requirements.pip
	virtualenv --distribute -p $(PYTHON) $(VENV)
	$(VENV)/bin/pip install -r test-requirements.pip || \
		(touch test-requirements.pip; exit 1)
	@touch $(VENV_ACTIVATE)

all: setup

check: test lint

clean:
	$(PYTHON) setup.py clean
	rm -rfv build/ dist/ juju_quickstart.egg-info MANIFEST
	rm -rfv $(VENV)
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -type d -delete

setup: $(VENV_ACTIVATE)

help:
	@echo -e 'Juju Quickstart - list of make targets:\n'
	@echo 'make sysdeps - Install the development environment system packages.'
	@echo 'make - Set up the development and testing environment.'
	@echo 'make test - Run tests.'
	@echo 'make lint - Run linter and pep8.'
	@echo 'make check - Run tests, linter and pep8.'
	@echo 'make source - Create source package.'
	@echo 'make install - Install on local system.'
	@echo 'make run - Run the application in the development environment.\n'
	@echo '  If "juju switch" has been used to set a default environment, that'
	@echo '  environment will be used. It is possible to override the default'
	@echo '  Juju environment by setting the JUJU_ENV environment variable,'
	@echo '  e.g.: "make run JUJU_ENV=ec2".'
	@echo 'make debug - Same as the "run" target but with the --debug flag.\n'
	@echo 'make clean - Get rid of bytecode files, build and dist dirs, venv.'
	@echo 'make release - Register and upload a release on PyPI.'

install:
	$(PYTHON) setup.py install
	rm -rfv ./build ./dist ./juju_quickstart.egg-info

lint: setup
	@$(VENV)/bin/flake8 --show-source --exclude=$(VENV) ./quickstart

release: check
	$(PYTHON) setup.py register sdist upload

run: setup
	$(VENV)/bin/python ./juju-quickstart

debug: setup
	$(VENV)/bin/python ./juju-quickstart --debug

source:
	$(PYTHON) setup.py sdist

sysdeps:
	sudo apt-get install --yes $(SYSDEPS)

test: setup
	@$(VENV)/bin/nosetests -s --verbosity=2 \
	    --with-coverage --cover-package=quickstart quickstart
	@rm .coverage

.PHONY: all clean check debug help install lint release run setup source \
	sysdeps test
