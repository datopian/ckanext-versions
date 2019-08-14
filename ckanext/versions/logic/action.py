# encoding: utf-8
import logging
from datetime import datetime

from ckan import model as core_model
from ckan.plugins import toolkit

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
    dataset_id, name = toolkit.get_or_bust(data_dict, ['dataset', 'name'])
    dataset = model.Package.get(dataset_id)
    if not dataset:
        raise toolkit.ObjectNotFound('Dataset not found')

    toolkit.check_access('dataset_version_create', context, data_dict)

    version = DatasetVersion(package_id=dataset.id,
                             package_revision_id=dataset.revision_id,
                             name=name,
                             description=data_dict.get('description', None),
                             created=datetime.utcnow(),
                             # TODO: is this right?
                             creator_user_id=context['user'])

    model.Session.add(version)
    model.repo.commit()

    log.info('Version "%s" created for package %s', name, dataset.id)

    return version.as_dict()


def dataset_version_list(context, data_dict):
    """List versions of a given dataset

    :param dataset: the id or name of the dataset
    :type dataset: string
    :returns: list of matched versions
    :rtype: list
    """
    model = context.get('model', core_model)
    dataset_id = toolkit.get_or_bust(data_dict, ['dataset'])
    dataset = model.Package.get(dataset_id)
    if not dataset:
        raise toolkit.ObjectNotFound('Dataset not found')

    toolkit.check_access('dataset_version_list', context, data_dict)

    versions = model.Session.query(DatasetVersion).\
        filter(DatasetVersion.package_id == dataset_id)

    return [v.as_dict() for v in versions]


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
