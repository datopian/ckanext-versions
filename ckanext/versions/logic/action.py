import logging
from ckan.plugins import toolkit as tk
from ckanext.versions.logic.schema import package_activity_create
from ckanext.versions.model import DatasetVersion
from sqlalchemy.exc import IntegrityError


log = logging.getLogger(__name__)


@tk.validate(package_activity_create)
def package_version_create(context, data_dict):
    """
    Create a new dataset version.
    :param context: The context dictionary
    :param package_id: The ID of the dataset
    :param activity_id: The ID of the activity
    :param name: The name of the version
    :param description: The description of the version
    :param creator_user_id: The ID of the user creating the version
    :return: The created version as a dictionary
    """
    tk.check_access("package_version_create", context, data_dict)

    version = DatasetVersion.create(
        package_id=data_dict["package_id"],
        activity_id=data_dict["activity_id"],
        name=data_dict["name"],
        description=data_dict.get("description"),
        creator_user_id=data_dict.get("creator_user_id"),
    )
    log.info(
        'Version "%s" created for dataset %s',
        data_dict["name"],
        data_dict["package_id"],
    )

    return version.as_dict()
