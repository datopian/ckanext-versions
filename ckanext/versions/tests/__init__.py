from ckan import model
from ckanext.versions.logic.dataset_version_action import dataset_version_create, dataset_version_restore
from ckanext.versions.model import create_tables, tables_exist


def versions_db_setup():
    if not tables_exist():
        create_tables()


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


def restore_version(dataset_id, version_id, user):
    context = get_context(user)
    return dataset_version_restore(context, {
        'dataset_id': dataset_id,
        'version_id': version_id
    })
