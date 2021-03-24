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

    :param dataset: the id or name of the dataset
    :type dataset: string
    :param version: the id of the version
    :type version: string
    :param name: A short name for the version
    :type name: string
    :param description: A description for the version
    :type description: string
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
    """Create a new version from the current dataset's revision

    Currently you must have editor level access on the dataset
    to create a version.

    :param package_id: the id or name of the dataset
    :type package_id: string
    :param resource: the id of the resource
    :type resource: string
    :param name: A short name for the version
    :type name: string
    :param notes: A description for the version
    :type notes: string
    :returns: the newly created version
    :rtype: dictionary
    """
    toolkit.check_access('version_create', context, data_dict)
    assert context.get('auth_user_obj')  # Should be here after `check_access`

    package_id, resource_id, name = toolkit.get_or_bust(
        data_dict, ['package_id', 'resource_id', 'name'])

    package = core_model.Package.get(package_id)
    if not package:
        raise toolkit.ObjectNotFound('Dataset not found')

    resource = core_model.Resource.get(resource_id)
    if not resource:
        raise toolkit.ObjectNotFound('Resource not found')

    session = core_model.meta.create_local_session()
    activity = session.query(core_model.Activity). \
        filter_by(object_id=data_dict['package_id']).\
        order_by(core_model.Activity.timestamp.desc()).\
        first()

    version = Version(
        package_id=data_dict['package_id'],
        resource_id=data_dict['resource_id'],
        activity_id=activity.id,
        name=data_dict.get('name', None),
        notes=data_dict.get('notes', None),
        created=datetime.utcnow(),
        creator_user_id=context['auth_user_obj'].id)

    session.add(version)

    try:
        session.commit()
    except IntegrityError as e:
        #  Name not unique, or foreign key constraint violated
        session.rollback()
        log.debug("DB integrity error (version name not unique?): %s", e)
        raise toolkit.ValidationError(
            'Version names must be unique per resource'
        )

    log.info('Version "%s" created for resource %s', data_dict['name'], data_dict['resource_id'])

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

    toolkit.check_access('version_list', context, data_dict)

    versions = model.Session.query(Version).\
        filter(Version.resource_id == resource.id).\
        order_by(Version.created.desc())

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
    toolkit.check_access('version_show', context, data_dict)
    model = context.get('model', core_model)
    version_id = toolkit.get_or_bust(data_dict, ['version_id'])
    version = model.Session.query(Version).get(version_id)
    if not version:
        raise toolkit.ObjectNotFound('Version not found')

    return version.as_dict()


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
