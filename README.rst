=============
ckanext-versions
=============

This CKAN extension adds an ability to create and manage named resources
versions in CKAN. Currently under development so there are no stable versions of it.

Internally, this extension will use CKAN's 2.9 activities to preserve
old revisions of metadata, and ensure uploaded data resources are unique
and do not replace or override each other as resources are modified.

Although the extension has it's own Uploader this extensions it is designed to be
used with `ckanext-blob-storage <https://github.com/datopian/ckanext-blob-storage>`_

As interface, this extension exposes a few new API actions described below. (no
UI work yet)

------------
Requirements
------------
ckanext-versions has been tested to work only with CKAN 2.9. It is not compatible
with CKAN 2.8 or older versions.

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

     ckan -c /etc/ckan/default/production.ini versions initdb

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

Note that for tests to run properly, you need to have this extension installed
in an environment that has CKAN installed in it, and configured to access a
local PostgreSQL and Solr instances.

You can specify the path to your local CKAN installation by adding::

    make test CKAN_PATH=../../src/ckan/

For example.

In addition, the following environment variables are useful when testing::

    CKAN_SQLALCHEMY_URL=postgres://ckan:ckan@my-postgres-db/ckan_test
    CKAN_SOLR_URL=http://my-solr-instance:8983/solr/ckan

