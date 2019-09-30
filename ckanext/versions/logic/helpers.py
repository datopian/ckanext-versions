from ckan.plugins import toolkit


def get_show_url(package_name, version):
    """Get the URL for 'package_show' for a version
    """
    dataset_id = "{}@{}".format(package_name, version['package_revision_id'])
    return toolkit.url_for('dataset_read',
                           id=dataset_id,
                           version=version['id'])
