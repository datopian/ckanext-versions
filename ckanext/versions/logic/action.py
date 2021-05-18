# encoding: utf-8
import difflib
import json
import logging
import re
from datetime import datetime

from ckan import model as core_model
from ckan.logic.action.get import resource_show as core_resource_show
from ckan.plugins import toolkit
from sqlalchemy.exc import IntegrityError

from ckanext.versions.model import Version

log = logging.getLogger(__name__)


def version_update(context, data_dict):
    """Update a version from the current dataset.

    :param package_id: the id the dataset
    :type package_id: string
    :param version_id: the id of the version
    :type version_id: string
    :param name: A short name for the version
    :type name: string
    :param notes: A description for the version
    :type notes: string
    :returns: the edited version
    :rtype: dictionary
    """
    model = context.get('model', core_model)
    version_id, name = toolkit.get_or_bust(data_dict, ['version', 'name'])

    # I'll create my own session! With Blackjack! And H**kers!
    session = model.meta.create_local_session()

    version = session.query(Version).\
        filter(Version.id == version_id).\
        one_or_none()

    if not version:
        raise toolkit.ObjectNotFound('Version not found')

    toolkit.check_access('dataset_version_create', context, data_dict)
    assert context.get('auth_user_obj')  # Should be here after `check_access`

    version.name = name
    version.description = data_dict.get('description', None)

    session.add(version)

    try:
        session.commit()
    except IntegrityError as e:
        #  Name not unique, or foreign key constraint violated
        session.rollback()
        log.debug("DB integrity error (version name not unique?): %s", e)
        raise toolkit.ValidationError(
            'Version names must be unique per dataset'
        )

    log.info('Version "%s" with id %s edited correctly', name, version_id)

    return version.as_dict()


def resource_version_create(context, data_dict):
    """Create a new version from the current dataset's activity_id

    Currently you must have editor level access on the dataset
    to create a version. If creator_user_id is not present, it will be set as
    the logged it user.

    :param resource_id: the id of the resource
    :type resource_id: string
    :param name: A short name for the version
    :type name: string
    :param notes optional: A description for the version
    :type notes: string
    :param creator_user_id optional: the id of the creator
    :type creator_user_id: string
    :returns: the newly created version
    :rtype: dictionary
    """
    model = context.get('model', core_model)

    resource_id, name = toolkit.get_or_bust(
        data_dict, ['resource_id', 'name'])

    resource = model.Resource.get(resource_id)
    if not resource:
        raise toolkit.ObjectNotFound('Resource not found')

    toolkit.check_access('version_create', context,
                         {"package_id": resource.package_id})

    creator_user_id = data_dict.get('creator_user_id')
    if creator_user_id:
        creator_user = model.User.get(creator_user_id)
        if not creator_user:
            raise toolkit.ObjectNotFound('Creator user not found')
    else:
        creator_user_id = context['auth_user_obj'].id

    activity = model.Session.query(model.Activity). \
        filter_by(object_id=resource.package_id). \
        order_by(model.Activity.timestamp.desc()).\
        first()

    version = Version(
        package_id=resource.package_id,
        resource_id=data_dict['resource_id'],
        activity_id=activity.id,
        name=name,
        notes=data_dict.get('notes', None),
        created=datetime.utcnow(),
        creator_user_id=creator_user_id)

    model.Session.add(version)

    try:
        model.Session.commit()
    except IntegrityError as e:
        #  Name not unique, or foreign key constraint violated
        model.Session.rollback()
        log.debug("DB integrity error (version name not unique?): %s", e)
        raise toolkit.ValidationError(
            'Version names must be unique per resource'
        )

    log.info(
        'Version "%s" created for resource %s',
        data_dict['name'],
        data_dict['resource_id']
        )

    return version.as_dict()


@toolkit.side_effect_free
def resource_version_list(context, data_dict):
    """List versions of a given resource

    :param resource_id: the id the resource
    :type resource_id: string
    :returns: list of matched versions
    :rtype: list
    """
    model = context.get('model', core_model)
    resource_id = toolkit.get_or_bust(data_dict, ['resource_id'])
    resource = model.Resource.get(resource_id)
    if not resource:
        raise toolkit.ObjectNotFound('Resource not found')

    toolkit.check_access('version_list', context,
                         {"package_id": resource.package_id})

    versions = model.Session.query(Version).\
        filter(Version.resource_id == resource.id).\
        order_by(Version.created.desc())

    if not versions:
        raise toolkit.ObjectNotFound('Versions not found for this resource')

    return [v.as_dict() for v in versions]


def version_delete(context, data_dict):
    """Delete a specific version

    :param version_id: the id of the version
    :type version_id: string
    :returns: The matched version
    :rtype: dict
    """
    model = context.get('model', core_model)
    version_id = toolkit.get_or_bust(data_dict, ['version_id'])
    version = model.Session.query(Version).get(version_id)
    if not version:
        raise toolkit.ObjectNotFound('Version not found')

    toolkit.check_access('version_delete', context,
                         {"package_id": version.package_id})

    model.Session.delete(version)
    model.repo.commit()

    log.info('Version %s was deleted', version_id)


@toolkit.side_effect_free
def version_show(context, data_dict):
    """Show a specific version object

    :param version_id: the id of the version
    :type version_id: string
    :returns: the version dictionary
    :rtype: dict
    """
    model = context.get('model', core_model)
    version_id = toolkit.get_or_bust(data_dict, ['version_id'])
    version = model.Session.query(Version).get(version_id)
    if not version:
        raise toolkit.ObjectNotFound('Version not found')

    toolkit.check_access('version_show', context,
                         {"package_id": version.package_id})

    return version.as_dict()


def resource_version_current(context, data_dict):
    ''' Show the current version for a resource

    :param resource_id: the if of the resource
    :type resource_id: string
    :returns the version dictionary
    :rtype dict
    '''
    version_list = resource_version_list(context, data_dict)
    return version_list[0]


def resource_history(context, data_dict):
    ''' Get an array with all the versions of the resource.

    In addition, each resource object in the array will contain an extra
    field called version, containing the version dictionary corresponding to
    that activity.

    :param resource_id: the id of the resource
    :type resource_id: string
    :returns array of resources
    :rtype array
    '''
    resource_id = toolkit.get_or_bust(data_dict, ['resource_id'])

    versions_list = resource_version_list(
        {'model': core_model, 'user': context['user']},
        {'resource_id': resource_id}
        )

    result = []
    for version in versions_list:
            resource = activity_resource_show(
                {'user': context['user']},
                {
                    'activity_id': version['activity_id'],
                    'resource_id': version['resource_id']
                }
                )
            resource['version'] = version
            result.append(resource)

    return result


def activity_resource_show(context, data_dict):
    ''' Returns a resource from the activity object.

    :param activity_id: the id of the activity
    :type activity_id: string
    :param resource_id: the id of the resource
    :type resource_id: string
    :returns: The resource in the activity
    :rtype: dict
    '''
    activity_id, resource_id = toolkit.get_or_bust(
        data_dict,
        ['activity_id', 'resource_id']
        )

    package = toolkit.get_action('activity_data_show')(
                {'model': core_model, 'user': context['user']},
                {'id': activity_id, 'object_type': 'package'}
                )
    old_resource = None
    for res in package['resources']:
        if res['id'] == resource_id:
            old_resource = res
            break

    if not old_resource:
        raise toolkit.NotFound('Resource not found in the activity object.')

    return old_resource


def _get_resource_in_revision(context, data_dict, revision_id):
    """Get resource from a given revision
    """
    current_revision_id = context.get('revision_id', None)
    context['revision_id'] = revision_id
    result = core_resource_show(context, data_dict)
    result['datastore_active'] = False
    _fix_resource_data(result, revision_id)

    if current_revision_id:
        context['revision_id'] = current_revision_id
    else:
        del context['revision_id']

    return result


def _fix_resource_data(resource_dict, revision_id):
    """Make some adjustments to the resource dict if we are showing a revision
    of a package
    """
    url = resource_dict.get('url')
    if url and resource_dict.get('url_type') == 'upload' and '://' in url:
        # Resource is pointing at a local uploaded file, which has already been
        # converted to an absolute URL by `model_dictize.resource_dictized`
        if resource_dict['id'] in url:
            rsc_id = '{}@{}'.format(resource_dict['id'], revision_id)
            url = url.replace(resource_dict['id'], rsc_id)

        if resource_dict['package_id'] in url:
            pkg_id = '{}@{}'.format(resource_dict['package_id'], revision_id)
            url = url.replace(resource_dict['package_id'], pkg_id)

        resource_dict['url'] = url

    return resource_dict


def _generate_diff(obj1, obj2, diff_type):

    def _dump_obj(obj):
        return json.dumps(obj, indent=2, sort_keys=True).split('\n')

    obj_lines = [_dump_obj(obj) for obj in [obj1, obj2]]

    if diff_type == 'unified':
        diff_generator = difflib.unified_diff(*obj_lines)
        diff = '\n'.join(line for line in diff_generator)
    elif diff_type == 'context':
        diff_generator = difflib.context_diff(*obj_lines)
        diff = '\n'.join(line for line in diff_generator)
    elif diff_type == 'html':
        # word-wrap lines. Otherwise you get scroll bars for most datasets.
        for obj_index in (0, 1):
            wrapped_obj_lines = []
            for line in obj_lines[obj_index]:
                wrapped_obj_lines.extend(re.findall(r'.{1,70}(?:\s+|$)', line))
            obj_lines[obj_index] = wrapped_obj_lines
        diff = difflib.HtmlDiff().make_table(*obj_lines)
    else:
        raise toolkit.ValidationError('diff_type not recognized')

    return diff


@toolkit.chained_action
def resource_view_list(up_func, context, data_dict):
    ''' Overrides core action to always return versions_view as the last view.

    Note: This will override the default order field for all the
    versions_view since it will force them to be displayed at the end.
    '''
    resource_views = up_func(context, data_dict)

    versions_views = []
    for i, view in enumerate(resource_views):
        if view['view_type'] == 'versions_view':
            versions_views.append(resource_views.pop(i))

    resource_views.extend(versions_views)

    return resource_views


def get_activity_id_from_resource_version_name(context, data_dict):
    ''' Returns the activity_id for the resource version

    :param resource_id: the id of the resource
    :type resource_id: string
    :param version: the name of the version
    :type version: string
    :returns: The activity_id of the version
    :rtype: string

    '''
    version_name = data_dict.get('version_name')
    version_list = resource_version_list(context, data_dict)

    for version in version_list:
        if version['name'] == version_name:
            return version['activity_id']

    raise toolkit.NotFound('Version not found in the resource.')


def resource_has_versions(context, data_dict):
    """Check if the resource has versions.

    :param resource_id: the id the resource
    :type resource_id: string
    :returns: True if the resource has at least 1 version
    :rtype: boolean
    """
    version_list = resource_version_list(context, data_dict)
    if not version_list:
        return False
    return True
