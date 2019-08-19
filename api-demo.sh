#!/usr/bin/env bash

API_KEY = "9f6f04ef-2dca-4028-8d6a-7a0019a2484b"

echo "Create a version for the current revision of my-version-dataset"
curl -H "Authorization: $API_KEY" -X POST http://ckan-dev:5000/api/3/action/dataset_version_create?dataset=my-version-dataset&name=Release01&description='initial release'



echo "List versions for the dataset"
curl -X GET http://ckan-dev:5000/api/3/action/dataset_version_list?dataset=my-version-dataset

# echo "Now user the revision in the version to get the dataset"
# curl -X GET http://ckan-dev:5000/api/3/action/package_show_revision?id=my-version-dataset&revision_id=<revision_id>
