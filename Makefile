# Makefile for ckanext-versions

PACKAGE_DIR := ckanext/versions

SHELL := bash
PIP := pip
ISORT := isort
FLAKE8 := flake8
PYTEST := pytest
SED := sed
CKAN := ckan

TEST_INI_PATH := ./test.ini
CKAN_PATH := ../ckan

TEST_PATH :=


test:
	$(PIP) install -r dev-requirements.txt
	$(ISORT) -rc -df -c $(PACKAGE_DIR)
	$(FLAKE8) $(PACKAGE_DIR)
	$(CKAN) -c $(TEST_INI_PATH) db init
	$(PYTEST) --ckan-ini=$(TEST_INI_PATH)  \
		  -s \
		  --cov=ckanext.versions \
		  --disable-warnings \
          ckanext/versions/tests/${TEST_PATH}
