PROJECT=jujuresources
PYTHON := /usr/bin/env python
SUITE=unstable
TESTS=tests/

all:
	@echo "make test"
	@echo "make source - Create source package"
	@echo "make clean"
	@echo "make userinstall - Install locally"
	@echo "make docs - Build html documentation"
	@echo "make release - Build and upload package and docs to PyPI"

source: setup.py
	scripts/update-revno
	python setup.py sdist

clean:
	-python setup.py clean
	find . -name '*.pyc' -delete
	rm -rf dist/*
	rm -rf .venv
#	rm -rf .venv3

userinstall:
	scripts/update-revno
	python setup.py install --user

.venv:
	sudo apt-get install -y gcc python-dev python-virtualenv python-apt
	virtualenv .venv --system-site-packages
	.venv/bin/pip install -U pip
	.venv/bin/pip install -I -r test_requirements.txt

#.venv3:
#	sudo apt-get install -y gcc python3-dev python-virtualenv python3-apt
#	virtualenv .venv3 --python=python3 --system-site-packages
#	.venv3/bin/pip install -U pip
#	.venv3/bin/pip install -I -r test_requirements.txt

# Note we don't even attempt to run tests if lint isn't passing.
test: lint test2 #test3

test2:
	@echo Starting Py2 tests...
	.venv/bin/nosetests -s --nologcapture tests/

#test3:
#	@echo Starting Py3 tests...
#	.venv3/bin/nosetests -s --nologcapture tests/

ftest: lint
	@echo Starting fast tests...
	.venv/bin/nosetests --attr '!slow' --nologcapture tests/
#	.venv3/bin/nosetests --attr '!slow' --nologcapture tests/

lint: .venv .venv3
	@echo Checking for Python syntax...
	@flake8 --max-line-length=120 $(PROJECT) $(TESTS) \
	    && echo Py2 OK
#	@python3 -m flake8.run --max-line-length=120 $(PROJECT) $(TESTS) \
#	    && echo Py3 OK

docs:
	- [ -z "`dpkg -l | grep python-sphinx`" ] && sudo apt-get install python-sphinx -y
	- [ -z "`dpkg -l | grep python-pip`" ] && sudo apt-get install python-pip -y
	- [ -z "`pip list | grep -i sphinx-pypi-upload`" ] && sudo pip install sphinx-pypi-upload
	cd docs && make html && cd -
.PHONY: docs

release: docs
	$(PYTHON) setup.py register sdist upload upload_docs
