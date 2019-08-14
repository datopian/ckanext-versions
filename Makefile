# Makefile for ckanext-versions

PACKAGE_DIR := ckanext/versions

SHELL := bash
PIP := pip
ISORT := isort
FLAKE8 := flake8
NOSETESTS := nosetests

TEST_INI_PATH := ./test.ini

test:
	$(PIP) install -r dev-requirements.txt
	$(ISORT) -rc -df -c $(PACKAGE_DIR)
	$(FLAKE8) $(PACKAGE_DIR)
	$(NOSETESTS) --ckan \
	      --with-pylons=$(TEST_INI_PATH) \
          --nologcapture \
          --with-doctest

coverage: test
	$(NOSETESTS) --ckan \
	      --with-pylons=$(TEST_INI_PATH) \
          --nologcapture \
		  --with-coverage \
          --cover-package=ckanext.versions \
          --cover-inclusive \
          --cover-erase \
          --cover-tests
