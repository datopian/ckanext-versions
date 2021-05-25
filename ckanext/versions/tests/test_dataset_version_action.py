import pytest

from ckan.plugins import toolkit
from ckan.tests import factories
from ckanext.versions.logic.dataset_version_action import dataset_version_create, dataset_has_versions
from ckanext.versions.tests import get_context


@pytest.mark.usefixtures('clean_db', 'versions_setup')
class TestDatasetVersion(object):

    def test_data_version_create(self, org_admin, test_dataset):
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

        self._assert_version(version, checks)

    @pytest.mark.parametrize("user_role, can_create_version", [
        ('admin', True),
        ('editor', True),
        ('member', False),
    ])
    def test_auth_version_create(self, test_organization, test_dataset, user_role, can_create_version):
        for user in test_organization['users']:
            if user['capacity'] == user_role:
                if can_create_version:
                    self._create_version(test_dataset['id'], user)
                else:
                    with pytest.raises(toolkit.NotAuthorized):
                        self._create_version(test_dataset['id'], user)
        pytest.fail("Couldn't find user with required role %s", user_role)

    def test_should_not_create_data_version_with_same_name(self, test_dataset, org_editor):
        version_name = "Not unique name"
        self._create_version(test_dataset['id'], org_editor, version_name=version_name)
        with pytest.raises(toolkit.ValidationError):
            self._create_version(test_dataset['id'], org_editor, version_name=version_name)

    def test_should_fail_if_dataset_not_exists(self, org_editor):
        with pytest.raises(toolkit.ObjectNotFound) as e:
            self._create_version('fake_dataset_id', org_editor)
            assert e.msg == "Dataset not found"

    def test_version_has_valid_activity_id(self, test_organization, org_editor):
        old_name = "Initial name"
        dataset = factories.Dataset(name=old_name, owner_org=test_organization['id'])
        version = self._create_version(dataset['id'], org_editor)
        context = get_context(org_editor)
        toolkit.get_action('package_patch')(
            context,
            {
                "id": dataset['id'],
                "name": "Updated Name"
            }
        )

        old_dataset = toolkit.get_action('activity_data_show')(
            context,
            {'id': version['activity_id']}
        )['package']

        assert old_dataset['name'] == old_name
        assert old_dataset['id'] == dataset['id']


    def test_new_dataset_has_no_versions(self, test_dataset, org_editor):
        context = get_context(org_editor)
        assert False == dataset_has_versions(
            context,
            {'id': test_dataset['id']}
        )

    def test_dataset_has_versions_after_one_created(self, test_dataset, org_editor):
        context = get_context(org_editor)
        self._create_version(test_dataset['id'], org_editor)
        assert True == dataset_has_versions(
            context,
            {'id': test_dataset['id']}
        )


    def _create_version(self, dataset_id, user, version_name="Default Name"):
        return dataset_version_create(
            get_context(user),
            {
                "dataset_id": dataset_id,
                "name": version_name
            }
        )

    def _assert_version(self, version, checks):
        assert version
        for k, v in checks:
            assert version[k] == v


@pytest.fixture()
def org_admin():
    return factories.User()


@pytest.fixture()
def org_editor():
    return factories.User()


@pytest.fixture()
def org_member():
    return factories.User()


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
