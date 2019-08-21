#!/usr/bin/env bash -x

# See https://docs.ckan.org/en/2.8/api/#authentication-and-api-keys
API_KEY=""

# Get the dataset ID
curl -H "Authorization: $API_KEY" "http://localhost:5000/api/3/action/package_show?name_or_id=my-version-dataset"

# Check that there are no versions for now
curl -H "Authorization: $API_KEY" "http://localhost:5000/api/3/action/dataset_version_list?dataset=f3860fa7-acd7-4c40-80c5-5c7a8f3c092f"

# Create a version for the current revision of my-version-dataset
curl -H "Authorization: $API_KEY" -X POST "http://localhost:5000/api/3/action/dataset_version_create" -d "dataset=my-version-dataset&name=Release01&description='initial release'"

# List versions for the dataset
curl -H "Authorization: $API_KEY" "http://localhost:5000/api/3/action/dataset_version_list?dataset=f3860fa7-acd7-4c40-80c5-5c7a8f3c092f"

# Show the revision in the version to get the dataset
curl -H "Authorization:$API_KEY" "http://ckan-dev:5000/api/3/action/package_show_revision?id=my-version-dataset&revision_id=7c91a05c-09fe-4713-9141-3033ef12c2d6"
