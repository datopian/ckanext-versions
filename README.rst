=============
ckanext-versions
=============

This CKAN extension adds an ability to create and manage named resources
versions in CKAN.

Internally, this extension will use CKAN's 2.9 activities to preserve
old revisions of metadata, and ensure uploaded data resources are unique
and do not replace or override each other as resources are modified.

This extension is designed to be used with
`ckanext-blob-storage <https://github.com/datopian/ckanext-blob-storage>`_

As interface, this extension exposes a few new API actions described below. (no
UI work)

------------
API Endpoints
------------

resource_version_create::

    curl -X POST -H "Authorization: $API_KEY" \
                    -H "Content-Type: application/json;charset=utf-8"
                    -d '{"resource_id": "9509ca60-a113-4d3b-8afa-83172b87368a", "name":"v1.0", "notes": "First Version."}'
                    -k "http://ckan:5000/api/action/resource_version_create"
    {
    "help": "http://ckan:5000/api/3/action/help_show?name=resource_version_create",
    "success": true,
    "result": {
        "id": "7eab640a-546a-4be1-97bf-9c7aa7a543ed",
        "package_id": "9a2ca5e4-1018-479d-8365-9e2f54c69d26",
        "resource_id": "9509ca60-a113-4d3b-8afa-83172b87368a",
        "activity_id": "2efbf349-5c66-4d4a-8c22-8dc31db7453a",
        "name": "v1.0",
        "notes": "First Version.",
        "creator_user_id": "62f05721-fb2f-453f-9816-702f9c9f76c6",
        "created": "2021-05-15 21:01:30.980231"
        }
    }

resource_version_list::

    curl -X POST -H "Authorization: $API_KEY"
                 -H "Content-Type: application/json;charset=utf-8"
                 -d '{"resource_id": "9509ca60-a113-4d3b-8afa-83172b87368a"}'
                 -k "http://ckan:5000/api/action/resource_version_list"
    {
    "help": "http://ckan:5000/api/3/action/help_show?name=resource_version_list",
    "success": true,
    "result": [
        {
        "id": "49a30927-d072-46c5-9602-f6388dfaf9c1",
        "package_id": "9a2ca5e4-1018-479d-8365-9e2f54c69d26",
        "resource_id": "9509ca60-a113-4d3b-8afa-83172b87368a",
        "activity_id": "2efbf349-5c66-4d4a-8c22-8dc31db7453a",
        "name": "v2.0",
        "notes": "Second Version.",
        "creator_user_id": "62f05721-fb2f-453f-9816-702f9c9f76c6",
        "created": "2021-05-15 21:10:57.069277"
        },
        {
        "id": "7eab640a-546a-4be1-97bf-9c7aa7a543ed",
        "package_id": "9a2ca5e4-1018-479d-8365-9e2f54c69d26",
        "resource_id": "9509ca60-a113-4d3b-8afa-83172b87368a",
        "activity_id": "2efbf349-5c66-4d4a-8c22-8dc31db7453a",
        "name": "v1.0",
        "notes": "First Version.",
        "creator_user_id": "62f05721-fb2f-453f-9816-702f9c9f76c6",
        "created": "2021-05-15 21:01:30.980231"
        }
      ]
    }

version_show::

    curl -X POST -H "Authorization: $API_KEY"
                 -H "Content-Type: application/json;charset=utf-8"
                 -d '{"version_id": "7eab640a-546a-4be1-97bf-9c7aa7a543ed"}'
                 -k "http://ckan:5000/api/action/version_show"
    {
    "help": "http://ckan:5000/api/3/action/help_show?name=version_show",
    "success": true,
    "result": {
        "id": "7eab640a-546a-4be1-97bf-9c7aa7a543ed",
        "package_id": "9a2ca5e4-1018-479d-8365-9e2f54c69d26",
        "resource_id": "9509ca60-a113-4d3b-8afa-83172b87368a",
        "activity_id": "2efbf349-5c66-4d4a-8c22-8dc31db7453a",
        "name": "v1.0",
        "notes": "First Version.",
        "creator_user_id": "62f05721-fb2f-453f-9816-702f9c9f76c6",
        "created": "2021-05-15 21:01:30.980231"
      }
    }

version_delete::

    curl -X POST -H "Authorization: $API_KEY"
                 -H "Content-Type: application/json;charset=utf-8"
                 -d '{"version_id": "7eab640a-546a-4be1-97bf-9c7aa7a543ed"}'
                 -k "http://ckan:5000/api/action/version_delete"
    {
    "help": "http://ckan:5000/api/3/action/help_show?name=version_delete",
    "success": true,
    "result": null
    }

resource_version_update::

    curl -X POST -H "Authorization: $API_KEY"
                 -H "Content-Type: application/json;charset=utf-8"
                 -d "version_id=7eab640a-546a-4be1-97bf-9c7aa7a543ed"
                 -d "name=v2.0"
                 -d "notes=New name for this version!"
                 -k "http://ckan:5000/api/action/version_delete"
    {
    "help": "http://ckan:5000/api/3/action/help_show?name=version_delete",
    "success": true,
    "result": {
        "id": "7eab640a-546a-4be1-97bf-9c7aa7a543ed",
        "package_id": "9a2ca5e4-1018-479d-8365-9e2f54c69d26",
        "resource_id": "9509ca60-a113-4d3b-8afa-83172b87368a",
        "activity_id": "2efbf349-5c66-4d4a-8c22-8dc31db7453a",
        "name": "v2.0",
        "notes": "New name for this version!",
        "creator_user_id": "62f05721-fb2f-453f-9816-702f9c9f76c6",
        "created": "2021-05-15 21:01:30.980231"
      }
    }

resource_version_patch::

    curl -X POST -H "Authorization: $API_KEY"
                 -H "Content-Type: application/json;charset=utf-8"
                 -d "version_id=7eab640a-546a-4be1-97bf-9c7aa7a543ed"
                 -d "notes=Updating only notes!"
                 -k "http://ckan:5000/api/action/version_delete"
    {
    "help": "http://ckan:5000/api/3/action/help_show?name=version_delete",
    "success": true,
    "result": {
        "id": "7eab640a-546a-4be1-97bf-9c7aa7a543ed",
        "package_id": "9a2ca5e4-1018-479d-8365-9e2f54c69d26",
        "resource_id": "9509ca60-a113-4d3b-8afa-83172b87368a",
        "activity_id": "2efbf349-5c66-4d4a-8c22-8dc31db7453a",
        "name": "v2.0",
        "notes": "Updating only notes!",
        "creator_user_id": "62f05721-fb2f-453f-9816-702f9c9f76c6",
        "created": "2021-05-15 21:01:30.980231"
      }
    }

------------
Download Endpoint
------------

To download the file for a specific version::

    /dataset/<dataset_id>/resource/<resource_id>/vervsion/<version_id>/download/

This extension also has a specific endpoint to download the file in previous
versions (only if the storage layer supports it). Internally it redirects to core
CKAN download endpoint with an extra query parameter for the activity_id.

Currently it works when using with `ckanext-blob-storage <https://github.com/datopian/ckanext-blob-storage>`_
but any other storage layer with support for activity_id can be used as well.


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

