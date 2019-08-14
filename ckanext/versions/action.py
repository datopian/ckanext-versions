# encoding: utf-8


def dataset_version_create(context, data_dict):
    """Create a new version from the current revision
    """
    pass


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
