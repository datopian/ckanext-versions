from ckan.plugins import toolkit


def get_show_url(package_name, version):
    """Get the URL for 'package_show' for a version
    """
    dataset_id = "{}@{}".format(package_name, version['package_revision_id'])
    return toolkit.url_for('dataset_read',
                           id=dataset_id,
                           version=version['id'])


def has_link_resources(package):
    """Return True if any resource in the dataset is a link to an external
    resource.
    """
    link_resource = any(resource['url_type'] is None
                        for resource in package.get('resources', []))

    return link_resource
