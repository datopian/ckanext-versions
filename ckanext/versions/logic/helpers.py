from ckan.plugins import toolkit

from ckanext.versions.lib.changes import (check_metadata_changes,
                                          check_resource_changes)


def get_show_url(package_name, version):
    """Get the URL for 'package_show' for a version
    """
    dataset_id = "{}@{}".format(package_name, version['package_revision_id'])
    return toolkit.url_for('dataset_read',
                           id=dataset_id,
                           version=version['id'])


def get_resource_show_url(package_name, resource_id, version):
    """Get the URL for 'package_show' for a version
    """
    extra_params = {}
    if version:
        dataset_id = "{}@{}".format(package_name,
                                    version['package_revision_id'])
        extra_params['version'] = version['id']
    else:
        dataset_id = package_name

    return toolkit.url_for(controller='package',
                           action='resource_read',
                           id=dataset_id,
                           resource_id=resource_id,
                           **extra_params)


def has_link_resources(package):
    """Return True if any resource in the dataset is a link to an external
    resource.
    """
    link_resource = any(
        resource['url_type'] is None or resource['url_type'] == ''
        for resource in package.get('resources', [])
    )

    return link_resource


def compare_pkg_dicts(old, new, old_activity_id):
    '''
    Takes two package dictionaries that represent consecutive versions of
    the same dataset and returns a list of detailed & formatted summaries of
    the changes between the two versions. old and new are the two package
    dictionaries. The function assumes that both dictionaries will have
    all of the default package dictionary keys, and also checks for fields
    added by extensions and extra fields added by the user in the web
    interface.

    Returns a list of dictionaries, each of which corresponds to a change
    to the dataset made in this revision. The dictionaries each contain a
    string indicating the type of change made as well as other data necessary
    to form a detailed summary of the change.
    '''
    change_list = []

    check_metadata_changes(change_list, old, new)

    check_resource_changes(change_list, old, new, old_activity_id)

    # if the dataset was updated but none of the fields we check were changed,
    # display a message stating that
    if len(change_list) == 0:
        change_list.append({u'type': 'no_change'})

    return change_list
