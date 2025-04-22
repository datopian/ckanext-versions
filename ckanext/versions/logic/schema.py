from ckan.plugins import toolkit as tk


@tk.validator_args
def package_activity_create(
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
        "activity_id": [not_empty, unicode_only],
        "description": [ignore_missing],
        "created": [ignore_missing, isodate],
        "creator_user_id": [ignore_missing, user_id_or_name_exists],
    }
