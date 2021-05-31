from ckan import model
from ckanext.versions.logic.dataset_version_action import dataset_version_create


def get_context(user):
    return {
        'model': model,
        'user': user if isinstance(user, str) else user['name']
    }


def assert_version(version, checks):
    assert version
    for k, v in checks.items():
        assert version[k] == v, "found incorrect %s of version" % k


def create_version(dataset_id, user, version_name="Default Name"):
    return dataset_version_create(
        get_context(user),
        {
            "dataset_id": dataset_id,
            "name": version_name
        }
    )