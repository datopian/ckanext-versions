from ckan.plugins import toolkit


def url_for_version(package_name, version=None, **kwargs):
    """Get the URL for a package / resource related action, with potential
    revision ID taken from a version info object

    If `version` is set, the version ID is appended to the package ID,
    and a ?version=... query parameter is added to URLs.

    If the `resource_id` parameter is provided and `version` is set, a
    revision ID will be appended to the resource_id.

    If the `route_name` parameter is provided, it will be used as the route
    name; Otherwise, `controller` and `action` are expected as arguments.
    """
    if version:
        package_name = "{}@{}".format(package_name,
                                      version['package_revision_id'])
        if 'version' not in kwargs:
            kwargs['version'] = version['id']

    if 'route_name' in kwargs:
        route = kwargs.pop('route_name')
        return toolkit.url_for(route, id=package_name, **kwargs)
    else:
        return toolkit.url_for(id=package_name, **kwargs)


def url_for_resource_version(package_name, version, **kwargs):
    """Similar to `url_for_version`, but also adds an "@revision" to the resource_id
    if it and a version is provided

    :param package_name:
    :param version:
    :param kwargs:
    :return:
    """
    if version and 'resource_id' in kwargs:
        kwargs['resource_id'] = "{}@{}".format(kwargs['resource_id'],
                                               version['package_revision_id'])

    return url_for_version(package_name, version, **kwargs)


def has_link_resources(package):
    """Return True if any resource in the dataset is a link to an external
    resource.
    """
    link_resource = any(
        resource['url_type'] is None or resource['url_type'] == ''
        for resource in package.get('resources', [])
        )

    return link_resource
