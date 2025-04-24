from ckan.authz import is_authorized
from ckan.plugins import toolkit as tk 


def package_version_create(context, data_dict):
    """Check if a user is allowed to create a version

    This is permitted only to users who are allowed to modify the dataset
    """
    return is_authorized('package_update', context,
                         {"id": data_dict['package_id']})


def package_version_show(context, data_dict):
    """Check if a user is allowed to update a version

    This is permitted only to users who are allowed to view the dataset
    """
    return is_authorized('package_show', context,
                         {"id": data_dict['id']})

def package_version_update(context, data_dict):
    """Check if a user is allowed to update a version

    This is permitted only to users who are allowed to modify the dataset
    """
    return is_authorized('package_update', context,
                         {"id": data_dict['package_id']})