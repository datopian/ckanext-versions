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
    """List all versions for a given dataset
    """
    return [
        {
            "id": "some-fake-id",
            "package_id": "some-fake-package-id",
            "package_revision_id": "more-fake-id",
            "name": "2019-10-01.1",
            "description": "Final data for the October 19' release",
            "craetor_user_id": "some-fake-user-id",
            "craeted": '2019-10-01 10:10:10:10'
         }
    ]


def dataset_version_delete(context, data_dict):
    """Delete a version
    """
    pass
