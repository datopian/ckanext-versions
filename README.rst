.. You should enable this project on travis-ci.org and coveralls.io to make
   these badges work. The necessary Travis and Coverage config files have been
   generated for you.

.. image:: https://travis-ci.org/datopian/ckanext-versions.svg?branch=master
    :target: https://travis-ci.org/datopian/ckanext-versions

.. image:: https://coveralls.io/repos/datopian/ckanext-versions/badge.svg
  :target: https://coveralls.io/r/datopian/ckanext-versions

.. image:: https://pypip.in/download/ckanext-versions/badge.svg
    :target: https://pypi.python.org/pypi//ckanext-versions/
    :alt: Downloads

.. image:: https://pypip.in/version/ckanext-versions/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-versions/
    :alt: Latest Version

.. image:: https://pypip.in/py_versions/ckanext-versions/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-versions/
    :alt: Supported Python versions

.. image:: https://pypip.in/status/ckanext-versions/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-versions/
    :alt: Development Status

.. image:: https://pypip.in/license/ckanext-versions/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-versions/
    :alt: License

=============
ckanext-versions
=============
This CKAN extension adds an ability to create and manage named dataset
versions in CKAN.

Currently it aims to implement an API only, as frontend functionality is
expected to be developed separately.

------------
Requirements
------------
ckanext-versions has been tested to work with CKAN 2.8. It may work with
other versions as well.

------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-versions:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-versions Python package into your virtual environment::

     pip install ckanext-versions

3. Add ``versions`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Initialize the database tables required for this extension by running::

     paster --plugin=ckanext-versions versions init-db

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload

---------------
Config Settings
---------------
This extension does not provide any additional configuration settings.

------------------------
Development Installation
------------------------

To install ckanext-versions for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/datopian/ckanext-versions.git
    cd ckanext-versions
    python setup.py develop
    pip install -r dev-requirements.txt


-----------------
Running the Tests
-----------------

To run the tests, do::

    make test

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    make test coverage

Note that for tests to run properly, you need to have this extension installed
in an environment that has CKAN installed in it, and configured to access a
local PostgreSQL instance.

You may need to edit ``test.ini`` and change the following line to point to the
path (relative to the location of ``test.ini``) of CKAN's configured INI file::

    [app:main]
    use = config:../../src/ckan/test-core.ini


