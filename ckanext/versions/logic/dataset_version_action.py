from ckan.plugins import toolkit


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
    pass


@toolkit.side_effect_free
def dataset_version_list(context, data_dict):
    """List versions of a given dataset

    :param dataset_id: the id of the dataset
    :type dataset_id: string
    :returns: list of versions created for the dataset
    :rtype: list
    """
    pass


@toolkit.side_effect_free
def dataset_version_latest(context, data_dict):
    ''' Show the latest version for a dataset

    :param dataset_id: the if of the dataset
    :type dataset_id: string
    :returns the version dictionary
    :rtype dict
    '''
    pass


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
