from ckan.authz import is_authorized
from ckan.plugins import toolkit as tk 


def package_version_create(context, data_dict):
    """Check if a user is allowed to create a version

    This is permitted only to users who are allowed to modify the dataset
    """
    return is_authorized('package_update', context,
                         {"id": data_dict['package_id']})

