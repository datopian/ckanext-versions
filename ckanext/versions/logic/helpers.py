from ckan.plugins import toolkit


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
        dataset_id = "{}@{}".format(package_name, version['package_revision_id'])
        extra_params['version'] = version['id']
    else:
        dataset_id = package_name

    return toolkit.url_for(controller='package',
                           action='resource_read',
                           id=dataset_id,
                           resource_id=resource_id,
                           **extra_params)
