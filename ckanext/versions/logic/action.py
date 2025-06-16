import logging
import json
import difflib
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
    existing_version = DatasetVersion.get(name=data_dict["name"], package_id=data_dict["package_id"])
    if existing_version:
        raise tk.ValidationError(
            f"Version with name '{data_dict['name']}' already exists."
        )

    version = DatasetVersion.create(
        package_id=data_dict["package_id"],
        name=data_dict["name"],
        notes=data_dict.get("notes"),
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
    data_dict["version_notes"] = dataset_version.notes
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
    notes = data_dict.get("version_notes")
    package_id = data_dict.get("id")
    existing_version = DatasetVersion.get(name=current_version, package_id=package_id)

    if existing_version:
        try:
            tk.get_action("package_version_update")(
                context,
                {
                    "id": existing_version.id,
                    "name": current_version,
                    "data": data_dict,
                    "notes": notes,
                },
            )
            log.info(
                "Version '%s' successfully updated for dataset %s.",
                current_version,
                data_dict.get("id"),
            )
        except tk.ValidationError as e:
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
                    "notes": notes,
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


@tk.side_effect_free
def package_version_diff(context, data_dict):
    """Returns a diff of the version, compared to the previous version of the
    object

    :param id: the id of the version
    :type id: string
    :param diff_type: 'unified', 'context', 'html'
    :type diff_type: string
    """

    model = context["model"]
    version_id = tk.get_or_bust(data_dict, "id")
    diff_type = data_dict.get("diff_type", "unified")

    tk.check_access("package_version_diff", context, data_dict)

    version = DatasetVersion.get(id=version_id)
    if version is None:
        raise tk.ObjectNotFound()
    prev_version = (
        model.Session.query(DatasetVersion)
        .filter(DatasetVersion.package_id == version.package_id)  # Filter by package_id
        .filter(DatasetVersion.created < version.created)  # Ensure it's an earlier version
        .order_by(DatasetVersion.created.desc())  # Order by creation date descending
        .first()
    )
    print("latest", version)
    print("preiv", prev_version)

    if prev_version is None:
        raise tk.ObjectNotFound("Previous version for this object not found")
    
    version_list = [prev_version, version]

    try:
        version_list = [
            vers.data for vers in version_list
        ]
    except KeyError:
        raise tk.ObjectNotFound("Could not find object in the version data")
    # convert each object dict to 'pprint'-style
    # and split into lines to suit difflib
    obj_lines = [
        json.dumps(ver, indent=2, sort_keys=True).split("\n") for ver in version_list
    ]

    # do the diff
    if diff_type == "unified":
        # type_ignore_reason: typechecker can't predict number of items
        diff_generator = difflib.unified_diff(*obj_lines)  # type: ignore
        diff = "\n".join(line for line in diff_generator)
    elif diff_type == "context":
        # type_ignore_reason: typechecker can't predict number of items
        diff_generator = difflib.context_diff(*obj_lines)  # type: ignore
        diff = "\n".join(line for line in diff_generator)
    elif diff_type == "html":
        # word-wrap lines. Otherwise you get scroll bars for most datasets.
        import re

        for obj_index in (0, 1):
            wrapped_obj_lines = []
            for line in obj_lines[obj_index]:
                wrapped_obj_lines.extend(re.findall(r".{1,70}(?:\s+|$)", line))
            obj_lines[obj_index] = wrapped_obj_lines
        # type_ignore_reason: typechecker can't predict number of items
        diff = difflib.HtmlDiff().make_table(*obj_lines)  # type: ignore
    else:
        raise tk.ValidationError({"message": "diff_type not recognized"})


    return {
        "diff": diff,
    }
