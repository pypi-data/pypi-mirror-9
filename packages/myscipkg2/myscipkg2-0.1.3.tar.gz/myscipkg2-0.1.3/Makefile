# Makefile for myscipkg2
PKG_NAME=myscipkg2
PKG_DIR=myscipkg2

VERSION := $(shell python setup.py --version)
GIT_VERSION_TAG := $(shell git describe --tags --dirty --always)

help:
	@echo "clean-build	remove build artifacts"
	@echo "clean-pyc	remove Python file artifacts"
	@echo "lint			check style with flake8"
	@echo "test 		run tests quickly with the default Python"
	@echo "coverage		check code coverage quickly with the default Python"
	@echo "docs			generate Sphinx HTML documentation, including API docs"
	@echo "release		package and upload a release"
	@echo "sdist		package"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	flake8 myscipkg2 test

test:
	python setup.py test

coverage:
	coverage run --source $(PKD_DIR) setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

docs:
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

release: clean test check-version check-version-tag
	python setup.py sdist bdist_wheel
	twine upload dist/*

# Check version string for PEP440 compatibility
# Requires the packaging package (pip install packaging)
check-version:
	python -c "from packaging.version import Version; Version('$(VERSION)')"
	@echo "Version okay."


ifeq ($(VERSION),$(GIT_VERSION_TAG))
check-version-tag:
	@echo "git tag okay"
else
check-version-tag:
	$(error "git tag ($(GIT_VERSION_TAG)) does not match setup.py version ($(VERSION))")
endif

# Helper if you need to figure out what packages are being imported
# Useful if Read the Docs is failing and you need to mock out more dependencies
find-imports:
	find $(PKG_DIR) -name "*.py" -exec fgrep "import" {} \; |  egrep '^(\s*)(import|from)' | sed 's/^\s+//' | tr -s ' ' | cut -d " " -f 2 | fgrep -v $(PKG_NAME) | sort -u | uniq

.PHONY: help clean clean-pyc check-version clean-build list test coverage docs release check-version-tag
