# encoding: utf-8
from ckan.logic.auth.get import package_show
from ckan.logic.auth.update import package_update


def dataset_version_create(context, data_dict):
    """Check if a user is allowed to create a version

    This is permitted only to users who are allowed to modify the dataset
    """
    return package_update(context, {"id": data_dict['dataset']})


def dataset_version_list(context, data_dict):
    """Check if a user is allowed to list dataset versions

    This is permitted only to users who can view the dataset
    """
    return package_show(context, {"id": data_dict['dataset']})


def dataset_version_delete(context, data_dict):
    """Check if a user is allowed to delete a version

    This is permitted only to users who are allowed to modify the dataset
    """
    return package_update(context, {"id": data_dict['dataset']})
