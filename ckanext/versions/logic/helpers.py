from ckan.plugins import toolkit


def dataset_version_get_show_url(package_name, version):
    """Get the URL for 'package_show' for a version
    """
    return toolkit.url_for('dataset_read',
                           id="{}@{}".format(package_name, version['package_revision_id']),
                           version=version['id'])
