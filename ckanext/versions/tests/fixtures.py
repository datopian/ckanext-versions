import pytest

from ckan.tests import factories
from ckanext.versions.model import create_tables, tables_exist
from ckanext.versions.tests import create_version


@pytest.fixture
def versions_setup():
    if not tables_exist():
        create_tables()

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

@pytest.fixture()
def test_version(test_dataset, org_editor):
    return create_version(test_dataset['id'], org_editor, version_name="Version1")
