.. image:: https://gitlab.com/datopian/ckanext-versions/badges/develop/pipeline.svg
    :target: https://gitlab.com/datopian/ckanext-versions/commits/develop

=============
ckanext-versions
=============
This CKAN extension adds an ability to create and manage named dataset
versions in CKAN.

Internally, this extension will use CKAN's VDM revisions to preserve
old revisions of metadata, and ensure uploaded data resources are unique
and do not replace or override each other as dataset resources are modified.

As interface, this extension exposes a minimal UI to access and manage
dataset versions, and a few new API actions described below.

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

-----------
API Actions
-----------
This extension exposes a number of new API actions to manage and use
dataset versions.

The HTTP method is GET for list / show actions and POST for create / delete
actions.

You will need to also pass in authentication information such as cookies or
tokens - you should consult the `CKAN API Guide
<https://docs.ckan.org/en/2.8/api/>`_ for details.

The following ``curl`` examples all assume the ``$API_KEY`` environment
variable is set and contains a valid CKAN API key, belonging to a user with
sufficient privileges; Output is indented and cleaned up for readability.

``dataset_version_list``
^^^^^^^^^^^^^^^^^^^^^^^^
List versions for a dataset.

**HTTP Method**: ``GET``

**Query Parameters**:

* ``dataset=<dataset_id>`` - The UUID or unique name of the dataset (required)

**Example**::

  $ curl -H "Authorization: $API_KEY" \
    https://ckan.example.com/api/3/action/dataset_version_list?dataset=my-awesome-dataset

  {
    "help": "http://ckan.example.com/api/3/action/help_show?name=dataset_version_list",
    "success": true,
    "result": [
      {
        "id": "5942ab7a-67cb-426c-ad99-dd4519530bc7",
        "package_id": "3b5a4f83-8770-4e8c-9630-c8abf6aa20f4",
        "package_revision_id": "7316fb6c-07e7-43b7-ade8-ac26c5693e6d",
        "name": "Version 1.2",
        "description": "Updated to include latest study results",
        "creator_user_id": "70587302-6a93-4c0a-bb3e-4d64c0b7c213",
        "created": "2019-10-27 15:29:53.452833"
      },
      {
        "id": "87d6f58a-a899-4f2d-88a4-c22e9e1e5dfb",
        "package_id": "3b5a4f83-8770-4e8c-9630-c8abf6aa20f4",
        "package_revision_id": "1b9fc99e-8e32-449e-85c2-24c893d9761e",
        "name": "Corrected for inflation",
        "description": "With Avi Bitter",
        "creator_user_id": "70587302-6a93-4c0a-bb3e-4d64c0b7c213",
        "created": "2019-10-27 15:29:16.070904"
      },
      {
        "id": "3e5601e2-1b39-43b6-b197-8040cc10036e",
        "package_id": "3b5a4f83-8770-4e8c-9630-c8abf6aa20f4",
        "package_revision_id": "e30ba6a8-d453-4395-8ee5-3aa2f1ca9e1f",
        "name": "Version 1.0",
        "description": "Added another resource with index of countries",
        "creator_user_id": "70587302-6a93-4c0a-bb3e-4d64c0b7c213",
        "created": "2019-10-27 15:24:25.248153"
      }
    ]
  }

``dataset_version_show``
^^^^^^^^^^^^^^^^^^^^^^^^
Show info about a specific dataset version.

Note that this will show the version information - not the dataset metadata or
data (see `package_show_version`_)

**HTTP Method**: ``GET``

**Query Parameters**:

 * ``id=<dataset_version_id>`` - The UUID of the version to show (required)

**Example**::

  $ curl -H "Authorization: $API_KEY" \
    https://ckan.example.com/api/3/action/dataset_version_show?id=5942ab7a-67cb-426c-ad99-dd4519530bc7

  {
    "help": "http://ckan.example.com/api/3/action/help_show?name=dataset_version_show",
    "success": true,
    "result": {
      "id": "5942ab7a-67cb-426c-ad99-dd4519530bc7",
      "package_id": "3b5a4f83-8770-4e8c-9630-c8abf6aa20f4",
      "package_revision_id": "7316fb6c-07e7-43b7-ade8-ac26c5693e6d",
      "name": "Version 1.2",
      "description": "Updated to include latest study results",
      "creator_user_id": "70587302-6a93-4c0a-bb3e-4d64c0b7c213",
      "created": "2019-10-27 15:29:53.452833"
    }
  }

``dataset_version_create``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Create a new version for the specified dataset *current* revision. You are
required to specify a name for the version, and can optionally specify a
description.

**HTTP Method**: ``POST``

**JSON Parameters**:

 * ``dataset=<dataset_id>`` - UUID or name of the dataset (required, string)
 * ``name``=<version_name>`` - Name for the version. Version names must be
   unique per dataset (required, string)
 * ``description=<description>`` - Long description for the version; Can be
   markdown formatted (optional, string)

**Example**::

  $ curl -H "Authorization: $API_KEY" \
         -H "Content-type: application/json" \
         -X POST \
         https://ckan.example.com/api/3/action/dataset_version_create \
         -d '{"dataset":"3b5a4f83-8770-4e8c-9630-c8abf6aa20f4", "name": "Version 1.3", "description": "With extra Awesome Sauce"}'

  {
    "help": "https://ckan.example.com/api/3/action/help_show?name=dataset_version_create",
    "success": true,
    "result": {
      "id": "e1a77b78-dfaf-4c05-a261-ff01af10d601",
      "package_id": "3b5a4f83-8770-4e8c-9630-c8abf6aa20f4",
      "package_revision_id": "96ad6e02-99cf-4598-ab10-ea80e864e505",
      "name": "Version 1.3",
      "description": "With extra Awesome Sauce",
      "creator_user_id": "70587302-6a93-4c0a-bb3e-4d64c0b7c213",
      "created": "2019-10-28 08:14:01.953796"
    }
  }

``dataset_version_delete``
^^^^^^^^^^^^^^^^^^^^^^^^^^
Delete a dataset version. This does not delete the metadata revision, just the
named version pointing to it, and any data not pointed to by any other version.

**HTTP Method**: ``POST``

**JSON Parameters**:

 * ``id=<dataset_version_id>`` - The UUID of the version to delete (required,
   string)

**Example**::

  $ curl -H "Authorization: $API_KEY" \
         -H "Content-type: application/json" \
         -X POST \
         https://ckan.example.com/api/3/action/dataset_version_delete \
         -d '{"id":"e1a77b78-dfaf-4c05-a261-ff01af10d601"}'

  {
    "help": "https://ckan.example.com/api/3/action/help_show?name=dataset_version_delete",
    "success": true,
    "result": null
  }

``package_show_version``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Show a dataset (AKA package) in a given version. This is identical to the
built-in ``package_show`` action, but shows dataset metadata for a given
version, and adds some versioning related metadata.

This is useful if you've used ``dataset_version_list`` to get all
named versions for a dataset, and now want to show that dataset in a specific
version.

If ``version_id`` is not specified, the latet version of the dataset will be
returned, but will include a list of versions for the dataset.

**HTTP Method**: ``GET``

**Query Parameters**:

 * ``id=<dataset_id>`` - The name or UUID of the dataset (required)
 * ``version_id=<version_id>`` - A version UUID to show (optional)

**Examples**:

Fetching dataset metadata in a specified version::

  $ curl -H "Authorization: $API_KEY" \
         'https://ckan.example.com/api/3/action/package_show_version?id=3b5a4f83-8770-4e8c-9630-c8abf6aa20f4&version_id=5942ab7a-67cb-426c-ad99-dd4519530bc7'

  {
    "help": "https://ckan.example.com/api/3/action/help_show?name=package_show_version",
    "success": true,
    "result": {
      "maintainer": "Bob Paulson",
      "relationships_as_object": [],
      "private": true,
      "maintainer_email": "",
      "num_tags": 2,

      "version_metadata": {
        "id": "5942ab7a-67cb-426c-ad99-dd4519530bc7",
        "package_id": "3b5a4f83-8770-4e8c-9630-c8abf6aa20f4",
        "package_revision_id": "7316fb6c-07e7-43b7-ade8-ac26c5693e6d",
        "name": "Version 1.2",
        "description": "Without Avi Bitter",
        "creator_user_id": "70587302-6a93-4c0a-bb3e-4d64c0b7c213",
        "created": "2019-10-27 15:29:53.452833"
      },

      "id": "3b5a4f83-8770-4e8c-9630-c8abf6aa20f4",
      "metadata_created": "2019-10-27T15:23:50.612130",
      "owner_org": "68f832f7-5952-4cac-8803-4af55c021ccd",
      "metadata_modified": "2019-10-27T20:14:42.564886",
      "author": "Joe Bloggs",
      "author_email": "",
      "state": "active",
      "version": "1.0",
      "type": "dataset",
      "resources": [
        {
          "cache_last_updated": null,
          "cache_url": null,
          "mimetype_inner": null,
          /// ... standard resource attributes ...
        }
      ],
      "num_resources": 1,

      /// ... more standard dataset attributes ...
    }
  }

Note the ``version_metadata``, which is only included with dataset metadata if
the ``version_id`` parameter was provided.

Fetching the current version of dataset metadata in a specified version::

  {
    "help": "https://ckan.example.com/api/3/action/help_show?name=package_show_version",
    "success": true,
    "result": {
      "license_title": "Green",
      "relationships_as_object": [],
      "private": true,
      "id": "3b5a4f83-8770-4e8c-9630-c8abf6aa20f4",
      "metadata_created": "2019-10-27T15:23:50.612130",
      "metadata_modified": "2019-10-27T20:14:42.564886",
      "author": "Joe Bloggs",
      "author_email": "",
      "state": "active",
      "version": "1.0",
      "creator_user_id": "70587302-6a93-4c0a-bb3e-4d64c0b7c213",
      "type": "dataset",
      "resources": [
        {
          "mimetype": "text/csv",
          "cache_url": null,
          "hash": "",
          "description": "",
          "name": "https://data.example.com/dataset/287f7e34-7675-49a9-90bd-7c6a8b55698e/resource.csv",
          "format": "CSV",
          /// ... standard resource attributes ...
        }
      ],
      "num_resources": 1,
      "tags": [
        {
          "vocabulary_id": null,
          "state": "active",
          "display_name": "bar",
          "id": "686198e2-7b9c-4986-bb19-3cf74cfe2552",
          "name": "bar"
        },
        {
          "vocabulary_id": null,
          "state": "active",
          "display_name": "foo",
          "id": "82259424-aec6-428c-a682-0b3f6b8ee67d",
          "name": "foo"
        }
      ],

      "versions": [
        {
          "id": "5942ab7a-67cb-426c-ad99-dd4519530bc7",
          "package_id": "3b5a4f83-8770-4e8c-9630-c8abf6aa20f4",
          "package_revision_id": "7316fb6c-07e7-43b7-ade8-ac26c5693e6d",
          "name": "Version 1.2",
          "description": "Fixed some inaccuracies in data",
          "creator_user_id": "70587302-6a93-4c0a-bb3e-4d64c0b7c213",
          "created": "2019-10-27 15:29:53.452833"
        },
        {
          "id": "87d6f58a-a899-4f2d-88a4-c22e9e1e5dfb",
          "package_id": "3b5a4f83-8770-4e8c-9630-c8abf6aa20f4",
          "package_revision_id": "1b9fc99e-8e32-449e-85c2-24c893d9761e",
          "name": "version 1.1",
          "description": "Adjusted for country-specific inflation",
          "creator_user_id": "70587302-6a93-4c0a-bb3e-4d64c0b7c213",
          "created": "2019-10-27 15:29:16.070904"
        }
      ],

      /// ... more standard dataset attributes ...
    }
  }


Note the ``version`` list, only included when showing the latest
dataset version via ``package_show_version``.

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

