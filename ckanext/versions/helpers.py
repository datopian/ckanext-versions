from ckan.plugins import toolkit


def resources_list_with_current_version(resources):
    '''Get the resource list and with name and url of the latest version.
    '''
    context = {'user': toolkit.c.user}
    for resource in resources:
        versions_list = toolkit.get_action('resource_version_list')(context, {
            'resource_id': resource['id']}
            )
        if versions_list:
           resource['version'] = versions_list[0]['name']
           resource['version_url'] = toolkit.url_for(
               'resource.read',
               id=versions_list[0]['package_id'],
               resource_id=versions_list[0]['resource_id'],
               activity_id=versions_list[0]['activity_id']
               )
    return resources


def resource_version_list(resource):
    '''Get the resource's version list
    '''
    context = {'user': toolkit.c.user}
    resource_version_list = toolkit.get_action('resource_version_list')(
        context, {'resource_id': resource['id']}
            )
    return resource_version_list


def resource_version_from_activity_id(resource, activity_id ):
    '''Get the resource version filtering for the given activity_id.

    '''
    context = {'user': toolkit.c.user}
    resource_version_list = toolkit.get_action('resource_version_list')(
        context, {'resource_id': resource['id']}
            )
    for version in resource_version_list:
        if version['activity_id'] == activity_id:
            return version
    return []


def resource_current_version(resource):
    '''Get the resource current version
    '''
    context = {'user': toolkit.c.user}
    versions_list = toolkit.get_action('resource_version_list')(context, {
            'resource_id': resource['id']}
            )
    if versions_list:
        current_version = toolkit.get_action('resource_version_current')(context, {
                'resource_id': resource['id']})
        return current_version
    return False
