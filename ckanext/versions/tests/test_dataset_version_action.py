import pytest

from ckan.plugins import toolkit
from ckan.tests import factories
from ckanext.versions.logic.dataset_version_action import (
    dataset_version_create,
    dataset_has_versions,
    get_activity_id_from_dataset_version_name,
    activity_dataset_show,
    dataset_version_latest, dataset_version_list
)
from ckanext.versions.tests import get_context


@pytest.mark.usefixtures('clean_db', 'versions_setup')
class TestDatasetVersion(object):

    def test_dataset_version_create_should_create_version(self, org_admin, test_dataset):
        version_name = "Test Version 1.0"
        version_notes = "Some details about the version"
        version = dataset_version_create(
            get_context(org_admin),
            {
                "dataset_id": test_dataset['id'],
                "name": version_name,
                "notes": version_notes
            }
        )
        checks = {'package_id': test_dataset['id'],
                  'resource_id': None,
                  'notes': version_notes,
                  'name': version_name,
                  'creator_user_id': org_admin['id']}

        _assert_version(version, checks)

    @pytest.mark.parametrize("user_role, can_create_version", [
        ('admin', True),
        ('editor', True),
        ('member', False),
    ])
    def test_dataset_version_create_auth(self, test_organization, test_dataset, user_role, can_create_version):
        for user in test_organization['users']:
            if user['capacity'] == user_role:
                if can_create_version:
                    _create_version(test_dataset['id'], user)
                    return
                else:
                    with pytest.raises(toolkit.NotAuthorized):
                        _create_version(test_dataset['id'], user)
                    return
        pytest.fail("Couldn't find user with required role %s", user_role)

    def test_dataset_version_create_should_not_create_version_with_same_name(self, test_dataset, org_editor):
        version_name = "Not unique name"
        _create_version(test_dataset['id'], org_editor, version_name=version_name)
        with pytest.raises(toolkit.ValidationError):
            _create_version(test_dataset['id'], org_editor, version_name=version_name)

    def test_dataset_version_create_should_fail_if_dataset_not_exists(self, org_editor):
        with pytest.raises(toolkit.ObjectNotFound) as e:
            _create_version('fake_dataset_id', org_editor)
            assert e.msg == "Dataset not found"

    def test_dataset_version_create_returns_valid_activity_id(self, test_organization, org_editor):
        old_name = "initial-name"
        dataset = factories.Dataset(name=old_name, owner_org=test_organization['id'])
        version = _create_version(dataset['id'], org_editor)
        context = get_context(org_editor)
        toolkit.get_action('package_patch')(
            context,
            {
                "id": dataset['id'],
                "name": "updated-name"
            }
        )

        old_dataset = toolkit.get_action('activity_data_show')(
            context,
            {'id': version['activity_id']}
        )['package']

        assert old_dataset['name'] == old_name
        assert old_dataset['id'] == dataset['id']

    def test_dataset_version_list_return_all_version(self, test_dataset, org_editor):
        context = get_context(org_editor)
        version1 = _create_version(test_dataset['id'], org_editor, version_name="Version1")
        toolkit.get_action('package_patch')(
            context,
            {
                "id": test_dataset['id'],
                "name": "updated-name"
            }
        )
        version2 = _create_version(test_dataset['id'], org_editor, version_name="Version2")

        version_list = dataset_version_list(
            context,
            {
                'dataset_id': test_dataset['id']
            }
        )
        version_ids = [v['id'] for v in version_list]
        assert version1['id'] in version_ids
        assert version2['id'] in version_ids

    def test_dataset_version_should_fail_if_dataset_not_exists(self, org_editor):
        context = get_context(org_editor)
        with pytest.raises(toolkit.ObjectNotFound) as e:
            dataset_version_list(
                context,
                {
                    'dataset_id': 'fake-dataset-id'
                }
            )
            assert "Dataset not found" == e.msg

    def test_dataset_version_should_return_empty_list_if_dataset_no_versions(self, test_dataset, org_editor):
        context = get_context(org_editor)
        versions_list = dataset_version_list(
            context,
            {
                'dataset_id': test_dataset['id']
            }
        )
        assert [] == versions_list

    def test_dataset_version_latest_show_latest_version(self, test_dataset, org_editor):
        context = get_context(org_editor)
        version1 = _create_version(test_dataset['id'], org_editor, version_name="Version1")
        toolkit.get_action('package_patch')(
            context,
            {
                "id": test_dataset['id'],
                "name": "updated-name"
            }
        )
        version2 = _create_version(test_dataset['id'], org_editor, version_name="Version2")

        latest_version = dataset_version_latest(
            context,
            {
                'dataset_id': test_dataset['id']
            }
        )

        assert version1['id'] != latest_version['id']
        _assert_version(latest_version, {'id': version2['id'], 'name': version2['name']})

    def test_dataset_version_latest_raises_when_dataset_not_found(self, org_editor):
        context = get_context(org_editor)
        with pytest.raises(toolkit.ObjectNotFound) as e:
            dataset_version_latest(
                context,
                {
                    'dataset_id': 'fake-dataset-id'
                }
            )
            assert "Dataset not found" == e.msg

    def test_dataset_version_latest_raises_when_dataset_has_no_versions(self, test_dataset, org_editor):
        context = get_context(org_editor)
        with pytest.raises(toolkit.ObjectNotFound) as e:
            dataset_version_latest(
                context,
                {
                    'dataset_id': test_dataset['id']
                }
            )
            assert "Versions not found in the dataset" == e.msg

    def test_activity_dataset_show_returns_correct_dataset(self, test_dataset, org_editor):
        version = _create_version(test_dataset['id'], org_editor)
        context = get_context(org_editor)
        updated_name = "Updated Name"
        new_dataset = toolkit.get_action('package_patch')(
            context,
            {
                "id": test_dataset['id'],
                "name": updated_name
            }
        )

        old_dataset = activity_dataset_show(
            context,
            {
                'dataset_id': new_dataset['id'],
                'activity_id': version['activity_id']
            }
        )

        assert test_dataset['name'] == old_dataset['name']
        assert new_dataset['id'] == old_dataset['id']

    def test_get_activity_id_from_dataset_version_returns_correct(self, test_dataset, org_editor):
        version = _create_version(test_dataset['id'], org_editor)
        expected_activity_id = version['activity_id']

        version = _create_version(test_dataset['id'], org_editor)

        context = get_context(org_editor)
        actual_activity_id = get_activity_id_from_dataset_version_name(
            context,
            {
                'dataset_id': test_dataset['id'],
                'version': version['name']
            }
        )

        assert expected_activity_id == actual_activity_id

    def test_get_activity_id_from_dataset_version_raises_not_found(self, org_editor):
        context = get_context(org_editor)
        with pytest.raises(toolkit.ObjectNotFound) as e:
            get_activity_id_from_dataset_version_name(
                context,
                {
                    'dataset_id': test_dataset['id'],
                    'version': 'Fake version name'
                }
            )
            assert "Version not found" == e.msg

    def test_new_dataset_has_no_versions(self, test_dataset, org_editor):
        context = get_context(org_editor)
        assert False == dataset_has_versions(
            context,
            {'id': test_dataset['id']}
        )

    def test_dataset_has_versions_after_one_created(self, test_dataset, org_editor):
        context = get_context(org_editor)
        _create_version(test_dataset['id'], org_editor)
        assert True == dataset_has_versions(
            context,
            {'id': test_dataset['id']}
        )


def _create_version(dataset_id, user, version_name="Default Name"):
    return dataset_version_create(
        get_context(user),
        {
            "dataset_id": dataset_id,
            "name": version_name
        }
    )


def _assert_version(version, checks):
    assert version
    for k, v in checks.items():
        assert version[k] == v


@pytest.fixture()
def org_admin():
    return factories.User(name="admin")


@pytest.fixture()
def org_editor():
    return factories.User(name="editor")


@pytest.fixture()
def org_member():
    return factories.User(name="member")


@pytest.fixture()
def test_organization(org_admin, org_editor, org_member):
    return factories.Organization(users=[
        {'name': org_admin['id'], 'capacity': 'admin'},
        {'name': org_editor['id'], 'capacity': 'editor'},
        {'name': org_member['id'], 'capacity': 'member'}
    ])


@pytest.fixture()
def test_dataset(test_organization):
    return factories.Dataset(owner_org=test_organization['id'])


@pytest.fixture()
def test_resource(test_dataset):
    return factories.Resource(package_id=test_dataset['id'])
