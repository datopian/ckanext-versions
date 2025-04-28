from ckan.plugins import toolkit as tk


@tk.validator_args
def package_version_create(
    unicode_only,
    not_empty,
    package_id_exists,
    ignore_missing,
    user_id_or_name_exists,
    isodate,
):
    """
    Create a new package activity.
    """
    return {
        "name": [not_empty, unicode_only],
        "package_id": [not_empty, unicode_only, package_id_exists],
        "notes": [ignore_missing],
        "created": [ignore_missing, isodate],
        "creator_user_id": [ignore_missing, user_id_or_name_exists],
    }


@tk.validator_args
def package_version_update(
    unicode_only,
    package_id_exists,
    ignore_missing,
    user_id_or_name_exists,
    isodate,
):
    """
    Create a new package activity.
    """
    return {
        "id": [ignore_missing, unicode_only],
        "name": [ignore_missing, unicode_only],
        "package_id": [ignore_missing, unicode_only, package_id_exists],
        "notes": [ignore_missing],
        "data": [ignore_missing],
        "created": [ignore_missing, isodate],
        "creator_user_id": [ignore_missing, user_id_or_name_exists],
    }
