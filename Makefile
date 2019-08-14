# Makefile for ckanext-versions

PACKAGE_DIR := ckanext/versions

SHELL := bash
PIP := pip
ISORT := isort
FLAKE8 := flake8
NOSETESTS := nosetests
SED := sed

TEST_INI_PATH := ./test.ini
CKAN_PATH := ../../src/ckan

prepare-config:
	$(SED) "s@use = config:.*@use = config:$(CKAN_PATH)/test-core.ini@" -i $(TEST_INI_PATH)

test: prepare-config
	$(PIP) install -r dev-requirements.txt
	$(ISORT) -rc -df -c $(PACKAGE_DIR)
	$(FLAKE8) $(PACKAGE_DIR)
	$(NOSETESTS) --ckan \
	      --with-pylons=$(TEST_INI_PATH) \
          --nologcapture \
          --with-doctest

coverage: prepare-config test
	$(NOSETESTS) --ckan \
	      --with-pylons=$(TEST_INI_PATH) \
          --nologcapture \
		  --with-coverage \
          --cover-package=ckanext.versions \
          --cover-inclusive \
          --cover-erase \
          --cover-tests
