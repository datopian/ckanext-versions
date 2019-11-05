# encoding: utf-8
import logging
from datetime import datetime

from ckan import model as core_model
from ckan.plugins import toolkit
from ckan.logic.action.get import package_show as core_package_show
from sqlalchemy.exc import IntegrityError

from ckanext.versions.model import DatasetVersion

log = logging.getLogger(__name__)


def dataset_version_create(context, data_dict):
    """Create a new version from the current dataset's revision

    Currently you must have editor level access on the dataset
    to create a version.

    :param dataset: the id or name of the dataset
    :type dataset: string
    :param name: A short name for the version
    :type name: string
    :param description: A description for the version
    :type description: string
    :returns: the newly created version
    :rtype: dictionary
    """
    model = context.get('model', core_model)
    dataset_id_or_name, name = toolkit.get_or_bust(
        data_dict, ['dataset', 'name'])
    dataset = model.Package.get(dataset_id_or_name)
    if not dataset:
        raise toolkit.ObjectNotFound('Dataset not found')

    toolkit.check_access('dataset_version_create', context, data_dict)
    assert context.get('auth_user_obj')  # Should be here after `check_access`

    latest_revision_id = dataset.latest_related_revision.id
    version = DatasetVersion(package_id=dataset.id,
                             package_revision_id=latest_revision_id,
                             name=name,
                             description=data_dict.get('description', None),
                             created=datetime.utcnow(),
                             creator_user_id=context['auth_user_obj'].id)

    # I'll create my own session! With Blackjack! And H**kers!
    session = model.meta.create_local_session()
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

    log.info('Version "%s" created for package %s', name, dataset.id)

    return version.as_dict()


@toolkit.side_effect_free
def dataset_version_list(context, data_dict):
    """List versions of a given dataset

    :param dataset: the id or name of the dataset
    :type dataset: string
    :returns: list of matched versions
    :rtype: list
    """
    model = context.get('model', core_model)
    dataset_id_or_name = toolkit.get_or_bust(data_dict, ['dataset'])
    dataset = model.Package.get(dataset_id_or_name)
    if not dataset:
        raise toolkit.ObjectNotFound('Dataset not found')

    toolkit.check_access('dataset_version_list', context, data_dict)

    versions = model.Session.query(DatasetVersion).\
        filter(DatasetVersion.package_id == dataset.id).\
        order_by(DatasetVersion.created.desc())

    return [v.as_dict() for v in versions]


@toolkit.side_effect_free
def dataset_version_show(context, data_dict):
    """Get a specific version by ID

    :param id: the id of the version
    :type id: string
    :returns: The matched version
    :rtype: dict
    """
    model = context.get('model', core_model)
    version_id = toolkit.get_or_bust(data_dict, ['id'])
    version = model.Session.query(DatasetVersion).get(version_id)
    if not version:
        raise toolkit.ObjectNotFound('Dataset version not found')

    toolkit.check_access('dataset_version_show', context,
                         {"dataset": version.package_id, "id": version_id})

    return version.as_dict()


def dataset_version_delete(context, data_dict):
    """Delete a specific version by ID

    :param id: the id of the version
    :type id: string
    :returns: The matched version
    :rtype: dict
    """
    model = context.get('model', core_model)
    version_id = toolkit.get_or_bust(data_dict, ['id'])
    version = model.Session.query(DatasetVersion).get(version_id)
    if not version:
        raise toolkit.ObjectNotFound('Dataset version not found')

    toolkit.check_access('dataset_version_delete', context,
                         {"dataset": version.package_id, "id": version_id})

    model.Session.delete(version)
    model.repo.commit()

    log.info('Version %s of dataset %s was deleted',
             version_id, version.package_id)


@toolkit.side_effect_free
def package_show_revision(context, data_dict):
    """Show a package from a specified revision

    Takes the same arguments as 'package_show' but with an additional
    revision ID parameter

    Revision ID can also be specified as part of the package ID, as
    <package_id>@<revision_id>.

    :param id: the id of the package
    :type id: string
    :param revision_id: the ID of the revision
    :type revision_id: string
    :returns: A package dict
    :rtype: dict
    """
    dd = data_dict.copy()
    if data_dict.get('revision_id') is None and '@' in data_dict['id']:
        package_id, revision_id = data_dict['id'].split('@', 1)
        dd.update({'id': package_id,
                   'revision_id': revision_id})
        return _get_package_in_revision(context, dd)
    else:
        return core_package_show(context, data_dict)


@toolkit.side_effect_free
def package_show_version(context, data_dict):
    """Wrapper for package_show with some additional version related info

    This works just like package_show but also optionally accepts `version_id`
    as a parameter; Providing it means that the returned data will show the
    package metadata from the specified version, and also include the
    version_metadata key with some version metadata.

    If version_id is not provided, package data will include a `versions` key
    with a list of versions for this package.
    """
    version_id = data_dict.get('version_id', None)
    if version_id:
        version_dict = dataset_version_show(context, {'id': version_id})
        dd = data_dict.copy()
        dd.update({'revision_id': version_dict['package_revision_id']})
        package_dict = _get_package_in_revision(context, dd)
        package_dict['version_metadata'] = version_dict

    else:
        package_dict = core_package_show(context, data_dict)
        versions = dataset_version_list(context,
                                        {'dataset': package_dict['id']})
        package_dict['versions'] = versions

    return package_dict


@toolkit.side_effect_free
def resource_show_version(context, data_dict):
    """Wrapper for resource_show allowing to get a resource from a specific
    dataset version
    """
    version_id = data_dict.get('version_id', None)
    if version_id:
        version_dict = dataset_version_show(context, {'id': version_id})
        resource_dict = _get_resource_in_revision(context, data_dict, version_dict['package_revision_id'])
        resource_dict['version_metadata'] = version_dict
        return resource_dict

    else:
        return toolkit.get_action('resource_show')(context, data_dict)


def _get_package_in_revision(context, data_dict):
    """Internal implementation of package_show_revision
    """
    revision_id = toolkit.get_or_bust(data_dict, ['revision_id'])
    current_revision_id = context.get('revision_id', None)
    context['revision_id'] = revision_id
    result = core_package_show(context, data_dict)

    if current_revision_id:
        context['revision_id'] = current_revision_id
    else:
        del context['revision_id']

    return result


def _get_resource_in_revision(context, data_dict, revision_id):
    """Get resource from a given revision
    """
    current_revision_id = context.get('revision_id', None)
    context['revision_id'] = revision_id
    result = toolkit.get_action('resource_show')(context, data_dict)

    if current_revision_id:
        context['revision_id'] = current_revision_id
    else:
        del context['revision_id']

    return result