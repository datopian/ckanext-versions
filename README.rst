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
API Actions
---------------
This extension exposes a number of new API actions to manage and use
dataset versions:

* ``dataset_version_list?dataset=<dataset_id>`` - List of versions for a
  given dataset. You can use the dataset's ID or name here.

* ``dataset_version_create?dataset=<dataset_id>&name=<version_name>&description=<description>`` -
  create a new version for the specified dataset current revision. You are
  required to specify a name for the version, and can optionally specify a
  description.

* ``dataset_version_show?id=<dataset_version_id>`` - show a specific dataset
  version. Note that this will show the version information - not the dataset
  metadata.

* ``dataset_version_delete?id=<dataset_version_id>`` - delete a dataset
  version. This does not delete the dataset / revision itself, just the named
  version pointing to it.

* ``package_show_revision?id=<dataset_id>&revision_id=<revision_id>`` - show
  a dataset (AKA package) from a given revision. This is exactly similar to the
  built-in ``package_show`` action, but shows dataset metadata for a given
  revision. This is useful if you've used ``dataset_version_list`` to get all
  named versions for a dataset, and now want to show that dataset for the given
  version.

To access any of the actions above, use the CKAN API action URL, for example::

    https://your-ckan-site.com/api/3/action/package_show_revision?id=warandpeace&dataset_revision_id=1e04e5d6-50d9-4c72-a20b-378b7d34050c

The HTTP method should be GET for list / show actions and POST for create /
delete actions.

You may need to also pass in authentication information such as cookies or
tokens - you should consult the `CKAN API Guide
<https://docs.ckan.org/en/2.8/api/>`_ for details.

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
local PostgreSQL and Solr instances.

You can specify the path to your local CKAN installation by adding::

    make test CKAN_PATH=../../src/ckan/

For example.

In addition, the following environment variables are useful when testing::

    CKAN_SQLALCHEMY_URL=postgres://ckan:ckan@my-postgres-db/ckan_test
    CKAN_SOLR_URL=http://my-solr-instance:8983/solr/ckan

