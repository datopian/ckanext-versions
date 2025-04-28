[![Tests](https://github.com//ckanext-versions/workflows/Tests/badge.svg?branch=main)](https://github.com//ckanext-versions/actions)

# ckanext-versions
This CKAN extension allows users to create and manage versions of datasets. It provides a versioning system that tracks changes made to datasets over time and also allows user to view and download previous versions.

## Installation
To install ckanext-versions:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com//ckanext-versions.git
    cd ckanext-versions
    pip install -e .
	pip install -r requirements.txt

3. Add `versions` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload

##  Working with Versions

### 1. Create the First Version
- **Set the Version**: In the dataset metadata, enter `Version: v1`.
- **Add Resources**: Upload your initial files.
- **Publish**: Save the dataset — this becomes **Version 1.0**.


### 2. Publish a New Version
- **Update the Version**: Edit the dataset metadata and change the version number to `v2` (or the next number).
- **Update/Add Resources**: Upload new files or update existing ones as needed.
- **Save**: Your changes are saved as **Version 2.0**.  
  *(Don't worry — previous versions stay accessible!)*


### 3. Edit Without Creating a New Version
- If you **edit** resources or metadata **without changing the version number**,  
  your updates will **overwrite** the current (latest) version.  
  *(No new version will be created.)*


```mermaid
flowchart TD
  start([Start])

  start --> create_v1[Create First Version]
  create_v1 --> set_v1[Set Version to v1]
  set_v1 --> upload_initial[Upload Initial Files]
  upload_initial --> publish_v1[Publish as Version 1.0]

  publish_v1 --> need_new_version{Is this a Major Update?}

  need_new_version -->|Yes| new_version[Create New Version]
  new_version --> change_version[Update Version Number to v2 or higher]
  change_version --> upload_new[Upload New or Updated Files]
  upload_new --> publish_new[Publish as New Version]

  need_new_version -->|No| edit_current[Edit Current Version]
  edit_current --> update_files[Improve dataset]
  update_files --> save_changes[Save Changes - No New Version]



## API Documentation

### `package_version_create`
**Description**: Creates a new version of a dataset.

**Parameters**:
- `package_id` (str): The ID of the dataset.
- `name` (str): The name of the version.
- `description` (str, optional): The description of the version.
- `creator_user_id` (str, optional): The ID of the user creating the version.

**Returns**: A dictionary representing the created version.


### `package_version_update`
**Description**: Updates an existing dataset version.

**Parameters**:
- `data_dict` (dict): Contains the version details to update.

**Returns**: A dictionary representing the updated version.


### `package_version_show`
**Description**: Retrieves details of a specific dataset version.

**Parameters**:
- `id` (str): The ID of the version.

**Returns**: A dictionary representing the version.

### `package_version_list`
**Description**: Lists all versions of a dataset.

**Parameters**:
- `package_id` (str): The ID of the dataset.

**Returns**: A list of dictionaries representing the versions.

### `package_version_delete`
**Description**: Deletes a specific dataset version.

**Parameters**:
- `id` (str): The ID of the version to delete.

**Returns**: A dictionary indicating success.


### `package_version_diff`
**Description**: Returns a diff of the current version compared to the previous version.

**Parameters**:
- `id` (str): The ID of the version.
- `diff_type` (str, optional): The type of diff (`unified`, `context`, or `html`).

**Returns**: A dictionary containing the diff.
