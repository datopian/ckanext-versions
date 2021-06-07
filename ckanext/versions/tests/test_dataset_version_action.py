import pytest

from ckan import model
from ckan.plugins import toolkit
from ckan.tests import factories
from ckanext.versions.logic.dataset_version_action import (
    dataset_version_create,
    dataset_has_versions,
    get_activity_id_from_dataset_version_name,
    activity_dataset_show,
    dataset_version_latest, dataset_version_list
)
from ckanext.versions.model import Version
from ckanext.versions.tests import get_context, assert_version, create_version, restore_version


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

        assert_version(version, checks)

    def test_dataset_create_version_accepts_dataset_name(self, test_dataset, org_editor):
        version = create_version(test_dataset['name'], org_editor)
        assert test_dataset['id'] == version['package_id']

    def test_dataset_create_should_create_version_for_given_activity(self, test_dataset, org_editor):
        version_name = "V1.0"
        context = get_context(org_editor)
        for i in range(2):
            toolkit.get_action('package_patch')(
                context,
                {
                    "id": test_dataset['id'],
                    "name": "updated-name%s" % i
                }
            )
        activities = toolkit.get_action('package_activity_list')(
            context,
            {
                'id': test_dataset['id']
            }
        )
        past_activity_id = activities[-1]['id']

        version = dataset_version_create(
            context,
            {
                "dataset_id": test_dataset['id'],
                "name": version_name,
                "activity_id": past_activity_id
            }
        )

        checks = {'package_id': test_dataset['id'],
                  'resource_id': None,
                  'notes': None,
                  'name': version_name,
                  'activity_id': past_activity_id,
                  'creator_user_id': org_editor['id']}

        assert_version(version, checks)

    def test_dataset_create_should_fail_when_incorrect_activity_id(self, test_dataset, org_editor):
        context = get_context(org_editor)
        with pytest.raises(toolkit.ObjectNotFound, match="Activity not found"):
            dataset_version_create(
                context,
                {
                    "dataset_id": test_dataset['id'],
                    "name": "V1.0",
                    "activity_id": "fake-activity-id"
                }
            )

    def test_dataset_version_create_fails_if_version_for_activity_exists(self, test_dataset, org_editor):
        create_version(test_dataset['id'], org_editor, version_name="Version1")
        with pytest.raises(toolkit.ValidationError, match="Version already exists for this activity"):
            create_version(test_dataset['id'], org_editor, version_name="Version2")


    @pytest.mark.parametrize("user_role, can_create_version", [
        ('admin', True),
        ('editor', True),
        ('member', False),
    ])
    def test_dataset_version_create_auth(self, test_organization, test_dataset, user_role, can_create_version):
        for user in test_organization['users']:
            if user['capacity'] == user_role:
                if can_create_version:
                    create_version(test_dataset['id'], user)
                    return
                else:
                    with pytest.raises(toolkit.NotAuthorized):
                        create_version(test_dataset['id'], user)
                    return
        pytest.fail("Couldn't find user with required role %s", user_role)

    def test_dataset_version_create_should_not_create_version_with_same_name(self, test_dataset, org_editor):
        version_name = "Not unique name"
        create_version(test_dataset['id'], org_editor, version_name=version_name)
        with pytest.raises(toolkit.ValidationError):
            create_version(test_dataset['id'], org_editor, version_name=version_name)

    def test_dataset_version_create_should_fail_if_dataset_not_exists(self, org_editor):
        with pytest.raises(toolkit.ObjectNotFound, match="Dataset not found"):
            create_version('fake_dataset_id', org_editor)

    def test_dataset_version_create_returns_valid_activity_id(self, test_organization, org_editor):
        old_name = "initial-name"
        dataset = factories.Dataset(name=old_name, owner_org=test_organization['id'])
        version = create_version(dataset['id'], org_editor)
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

    @pytest.mark.parametrize("object_ref", [
        "id",
        "name"
    ])
    def test_dataset_version_restore_retrives_dataset(self, test_version, test_dataset, org_editor, object_ref):
        context = get_context(org_editor)
        dataset_title = test_dataset['title']
        dataset_id = test_dataset['id']
        dataset_ref = test_dataset[object_ref]
        version_ref = test_version[object_ref]
        toolkit.get_action('package_patch')(
            context,
            {
                "id": dataset_id,
                "title": "updated-title"
            }
        )
        restored_dataset = restore_version(dataset_ref, version_ref, org_editor)

        assert dataset_title == restored_dataset['title'], "restored dataset title does not match"
        assert dataset_id == restored_dataset['id'], "restored dataset has different id"

    def test_dataset_version_restore_creates_new_version_after_restore(self, test_version, test_dataset, org_editor):
        restore_version(test_dataset['id'], test_version['id'], org_editor)
        latest_version = model.Session.query(Version). \
            filter(Version.package_id == test_dataset['id']). \
            order_by(Version.created.desc()).first()

        assert latest_version.id != test_version['id'], "restore action should create a new version"

    def test_dataset_version_restore_fails_if_dataset_not_found(self, test_version, test_dataset, org_editor):
        with pytest.raises(toolkit.ObjectNotFound, match="Dataset not found"):
            restore_version('fake-dataset-id', test_version['id'], org_editor)

    def test_dataset_version_restore_fails_if_dataset_not_have_version(self, test_version, test_dataset, org_editor):
        with pytest.raises(toolkit.ObjectNotFound, match="Version not found"):
            restore_version(test_dataset['id'], 'fake-version-id', org_editor)

    @pytest.mark.parametrize("user_role, can_create_version", [
        ('admin', True),
        ('editor', True),
        ('member', False),
    ])
    def test_dataset_version_restore_auth(self, test_version, test_organization, test_dataset, user_role, can_create_version):
        for user in test_organization['users']:
            if user['capacity'] == user_role:
                if can_create_version:
                    restore_version(test_dataset['id'], test_version['id'], user)
                    return
                else:
                    with pytest.raises(toolkit.NotAuthorized):
                        restore_version(test_dataset['id'], test_version['id'], user)
                    return
        pytest.fail("Couldn't find user with required role %s", user_role)

    def test_dataset_version_list_return_all_version(self, test_dataset, org_editor):
        context = get_context(org_editor)
        version1 = create_version(test_dataset['id'], org_editor, version_name="Version1")
        toolkit.get_action('package_patch')(
            context,
            {
                "id": test_dataset['id'],
                "name": "updated-name"
            }
        )
        version2 = create_version(test_dataset['id'], org_editor, version_name="Version2")

        version_list = dataset_version_list(
            context,
            {
                'dataset_id': test_dataset['id']
            }
        )
        version_ids = [v['id'] for v in version_list]
        assert 2 == len(version_ids), "only 2 versions created for dataset"
        assert version1['id'] in version_ids
        assert version2['id'] in version_ids

    def test_dataset_version_list_return_version_in_create_time_desc_order(self, test_dataset, org_editor):
        context = get_context(org_editor)
        version1 = create_version(test_dataset['id'], org_editor, version_name="Version1")
        toolkit.get_action('package_patch')(
            context,
            {
                "id": test_dataset['id'],
                "title": "New Title"
            }
        )
        version2 = create_version(test_dataset['id'], org_editor, version_name="Version2")

        version_list = dataset_version_list(
            context,
            {
                'dataset_id': test_dataset['id']
            }
        )
        assert version2['id'] == version_list[0]['id'], "version2 should be first as newest"
        assert version1['id'] == version_list[-1]['id'], "version1 should be last as oldest"

    def test_dataset_version_should_fail_if_dataset_not_exists(self, org_editor):
        context = get_context(org_editor)
        with pytest.raises(toolkit.ObjectNotFound, match="Dataset not found"):
            dataset_version_list(
                context,
                {
                    'dataset_id': 'fake-dataset-id'
                }
            )

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
        version1 = create_version(test_dataset['id'], org_editor, version_name="Version1")
        toolkit.get_action('package_patch')(
            context,
            {
                "id": test_dataset['id'],
                "name": "updated-name"
            }
        )
        version2 = create_version(test_dataset['id'], org_editor, version_name="Version2")

        latest_version = dataset_version_latest(
            context,
            {
                'dataset_id': test_dataset['id']
            }
        )

        assert version1['id'] != latest_version['id']
        assert_version(latest_version, {'id': version2['id'], 'name': version2['name']})

    def test_dataset_version_latest_raises_when_dataset_not_found(self, org_editor):
        context = get_context(org_editor)
        with pytest.raises(toolkit.ObjectNotFound, match="Dataset not found"):
            dataset_version_latest(
                context,
                {
                    'dataset_id': 'fake-dataset-id'
                }
            )

    def test_dataset_version_latest_raises_when_dataset_has_no_versions(self, test_dataset, org_editor):
        context = get_context(org_editor)
        with pytest.raises(toolkit.ObjectNotFound, match="Versions not found for this dataset"):
            dataset_version_latest(
                context,
                {
                    'dataset_id': test_dataset['id']
                }
            )

    def test_activity_dataset_show_returns_correct_dataset(self, test_dataset, org_editor):
        version = create_version(test_dataset['id'], org_editor)
        context = get_context(org_editor)
        updated_name = "updated-name"
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

    def test_activity_dataset_show_fails_if_no_dataset_in_activity(self, test_dataset, org_editor):
        version = create_version(test_dataset['id'], org_editor)
        context = get_context(org_editor)
        with pytest.raises(toolkit.ObjectNotFound, match='Dataset not found in the activity object.'):
            activity_dataset_show(
                context,
                {
                    'dataset_id': 'fake-dataset-id',
                    'activity_id': version['activity_id']
                }
            )

    def test_get_activity_id_from_dataset_version_returns_correct(self, test_dataset, org_editor):
        version1 = create_version(test_dataset['id'], org_editor, version_name="Version1")
        expected_activity_id = version1['activity_id']

        context = get_context(org_editor)
        actual_activity_id = get_activity_id_from_dataset_version_name(
            context,
            {
                'dataset_id': test_dataset['id'],
                'version': version1['name']
            }
        )

        assert expected_activity_id == actual_activity_id

    def test_get_activity_id_from_dataset_version_raises_not_found(self, test_dataset, org_editor):
        context = get_context(org_editor)
        with pytest.raises(toolkit.ObjectNotFound, match="Version not found in the dataset"):
            get_activity_id_from_dataset_version_name(
                context,
                {
                    'dataset_id': test_dataset['id'],
                    'version': 'Fake version name'
                }
            )

    def test_new_dataset_has_no_versions(self, test_dataset, org_editor):
        context = get_context(org_editor)
        assert False is dataset_has_versions(
            context,
            {'dataset_id': test_dataset['id']}
        )

    def test_dataset_has_versions_after_one_created(self, test_dataset, org_editor):
        context = get_context(org_editor)
        create_version(test_dataset['id'], org_editor)
        assert True is dataset_has_versions(
            context,
            {'dataset_id': test_dataset['id']}
        )
