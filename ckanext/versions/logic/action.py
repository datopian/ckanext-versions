import logging
from ckan.plugins import toolkit as tk
from ckanext.versions.logic.schema import package_version_create, package_version_update
from ckanext.versions.model import DatasetVersion

log = logging.getLogger(__name__)


@tk.validate(package_version_create)
def package_version_create(context, data_dict):
    """
    Create a new dataset version.
    :param context: The context dictionary
    :param package_id: The ID of the dataset
    :param name: The name of the version
    :param description: The description of the version
    :param creator_user_id: The ID of the user creating the version
    :return: The created version as a dictionary
    """
    tk.check_access("package_version_create", context, data_dict)

    package_dict = tk.get_action("package_show")(
        context,
        {
            "id": data_dict["package_id"],
        },
    )

    # Check if the version already exists
    existing_version = DatasetVersion.get(name=data_dict["name"])
    if existing_version:
        raise tk.ValidationError(
            f"Version with name '{data_dict['name']}' already exists."
        )

    version = DatasetVersion.create(
        package_id=data_dict["package_id"],
        name=data_dict["name"],
        description=data_dict.get("description"),
        data=package_dict,
        creator_user_id=package_dict.get("creator_user_id"),
    )

    log.info(
        'Version "%s" created for dataset %s',
        data_dict["name"],
        data_dict["package_id"],
    )
    return version.as_dict()


@tk.validate(package_version_update)
def package_version_update(context, data_dict):
    """
    Update an existing dataset version.
    :param context: The context dictionary
    :param data_dict: The data dictionary containing the version details
    :return: The updated version as a dictionary
    """
    tk.check_access("package_version_update", context, data_dict)
    version = DatasetVersion.update(**data_dict)
    return version.as_dict()


@tk.side_effect_free
def package_version_show(context, data_dict):
    """
    Show a specific version of a dataset.
    :param context: The context dictionary
    :param data_dict: The data dictionary containing the version details
    :return: The version as a dictionary
    """

    dataset_version = DatasetVersion.get(id=data_dict["id"])
    if not dataset_version:
        raise tk.ObjectNotFound(
            f"Dataset version with ID '{data_dict['id']}' not found."
        )
    try:
        tk.check_access("package_version_show", context, {"id": dataset_version.package_id})
    except  Exception as e:
        print(e)
    data_dict = dataset_version.as_dict().get("data", {})
    data_dict["version_id"] = dataset_version.id
    data_dict["version_description"] = dataset_version.description
    return data_dict


@tk.side_effect_free
def package_version_list(context, data_dict):
    tk.check_access("package_version_list", context, data_dict)
    package_id = data_dict.get("package_id")
    if not package_id:
        raise tk.ValidationError("Dataset ID is required.")
    versions = DatasetVersion.get_all(package_id=package_id)
    return [version.as_dict() for version in versions]


def package_version_delete(context, data_dict):
    """
    Delete a specific version of a dataset.
    :param context: The context dictionary
    :param data_dict: The data dictionary containing the version details
    :return: None
    """
    tk.check_access("package_version_delete", context, data_dict)
    if not data_dict.get("id"):
        raise tk.ValidationError("Version ID is required.")

    version = DatasetVersion.get(id=data_dict["id"])
    if not version:
        raise tk.ObjectNotFound(
            f"Dataset version with ID '{data_dict['id']}' not found."
        )
    version.delete()
    log.info(
        'Version "%s" deleted for dataset %s',
        version.name,
        version.package_id,
    )
    return {"success": True}


@tk.chained_action
def package_update(up_func, context, data_dict):
    """
    Update a package and create a new version if the version has changed.
    :param up_func: The function to update the package
    :param context: The context dictionary
    :param data_dict: The data dictionary containing the package details
    :return: The updated package as a dictionary
    """
    result = up_func(context, data_dict)
    _version_create_or_update(context, result)
    return result


def _version_create_or_update(context, data_dict):
    """
    Create or update a dataset version based on the provided data.
    :param context: The context dictionary
    :param data_dict: The data dictionary containing version details
    """
    current_version = data_dict.get("version")

    if getattr(tk.g, "update_version", False):

        try:
            tk.get_action("package_version_update")(
                context,
                {
                    "name": current_version,
                    "data": data_dict,
                },
            )
            log.info(
                "Version '%s' successfully updated for dataset %s.",
                current_version,
                data_dict.get("id"),
            )
        except tk.ValidationError as e:
            print(e)
            raise tk.ValidationError(
                {
                    "error": [f"Version with name '{current_version}' already exists."],
                }
            )

    else:
        try:
            tk.get_action("package_version_create")(
                context,
                {
                    "package_id": data_dict.get("id"),
                    "name": current_version,
                    "description": data_dict.get("description"),
                    "creator_user_id": data_dict.get("creator_user_id"),
                },
            )
            log.info(
                "Version '%s' successfully created for dataset %s.",
                current_version,
                data_dict.get("id"),
            )
        except tk.ValidationError as e:
            raise tk.ValidationError(
                {
                    "error": [f"Version with name '{current_version}' already exists."],
                }
            )
        except Exception as e:
            print(e)
            raise tk.ValidationError(
                {
                    "message": ["Error creating version"],
                }
            )


@tk.side_effect_free
def package_version_exists(context, data_dict):
    """
    Check if a specific version of a dataset exists.
    :param context: The context dictionary
    :param data_dict: The data dictionary containing the version details
    :return: True if the version exists, False otherwise
    """
    if not data_dict.get("name") or not data_dict.get("package_id"):
        raise tk.ValidationError("Version name and package ID are required.")

    tk.check_access("package_version_list", context, data_dict)
    version = DatasetVersion.get(
        name=data_dict["name"], package_id=data_dict["package_id"]
    )
    if not version:
        return {"exists": False}
    return {"exists": True}

