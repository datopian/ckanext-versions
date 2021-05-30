import logging

from datetime import datetime
from sqlalchemy.exc import IntegrityError

from ckan import model as core_model
from ckan.plugins import toolkit
from ckanext.versions.model import Version

log = logging.getLogger(__name__)

def dataset_version_create(context, data_dict):
    """Create a new version from the current dataset's activity_id

    Currently you must have editor level access on the dataset
    to create a version. If creator_user_id is not present, it will be set as
    the logged it user.

    :param dataset_id: the id of the dataset
    :type dataset_id: string
    :param name: A short name for the version, e.g. v1.0
    :type name: string
    :param notes optional: Notes about the version
    :type notes: string
    :returns: the newly created version
    :rtype: dictionary
    """
    model = context.get('model', core_model)
    dataset_id, name = toolkit.get_or_bust(
        data_dict, ['dataset_id', 'name'])

    dataset = model.Package.get(dataset_id)
    if not dataset:
        raise toolkit.ObjectNotFound("Dataset not found")

    toolkit.check_access('version_create',
                         context,
                         {"package_id": dataset_id} )
    creator_user_id = context['auth_user_obj'].id

    # TODO: add support for specific activity_id in data_dict
    activity = model.Session.query(model.Activity). \
        filter_by(object_id=dataset_id). \
        order_by(model.Activity.timestamp.desc()). \
        first()

    if not activity:
        # TODO: Add test for this exception
        raise toolkit.ObjectNotFound('Activity not found')

    version = Version(
        package_id=dataset_id,
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
            'Version names must be unique per dataset'
        )

    log.info(
        'Version "%s" created for dataset %s',
        name,
        dataset_id
    )

    return version.as_dict()


@toolkit.side_effect_free
def dataset_version_list(context, data_dict):
    """List versions of a given dataset

    :param dataset_id: the id of the dataset
    :type dataset_id: string
    :returns: list of versions created for the dataset
    :rtype: list
    """
    model = context.get('model', core_model)
    dataset_id = toolkit.get_or_bust(data_dict, ['dataset_id'])
    dataset = model.Package.get(dataset_id)
    if not dataset:
        raise toolkit.ObjectNotFound('Dataset not found')

    toolkit.check_access('version_list', context,
                         {"package_id": dataset_id})

    versions = model.Session.query(Version). \
        filter(Version.package_id == dataset.id). \
        order_by(Version.created.desc())

    return [v.as_dict() for v in versions]


@toolkit.side_effect_free
def dataset_version_latest(context, data_dict):
    ''' Show the latest version for a dataset

    :param dataset_id: the if of the dataset
    :type dataset_id: string
    :returns the version dictionary
    :rtype dict
    '''
    version_list = dataset_version_list(context, data_dict)
    if len(version_list) < 1:
        raise toolkit.ObjectNotFound("Versions not found for this dataset")
    return version_list[0]


def activity_dataset_show(context, data_dict):
    ''' Returns a dataset from the activity object.

    :param activity_id: the id of the activity
    :type activity_id: string
    :param dataset_id: the id of the resource
    :type dataset_id: string
    :returns: The dataset in the activity
    :rtype: dict
    '''
    pass


def get_activity_id_from_dataset_version_name(context, data_dict):
    ''' Returns the activity_id for the dataset version

    :param dataset_id: the id of the resource
    :type dataset_id: string
    :param version: the name or id of the version
    :type version: string
    :returns: The activity_id of the version
    :rtype: string

    '''
    pass


def dataset_has_versions(context, data_dict):
    """Check if the dataset has versions.

    :param dataset_id: the id the dataset
    :type dataset_id: string
    :returns: True if the dataset has at least 1 version
    :rtype: boolean
    """
    pass
