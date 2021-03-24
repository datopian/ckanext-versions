import pytest
from ckan import model
from ckan.plugins import toolkit
from ckan.tests import factories

from ckanext.versions.logic.action import resource_version_create
from ckanext.versions.tests import get_context


@pytest.mark.usefixtures("clean_db", "versions_setup")
class TestCreateResourceVersion(object):

    def test_resource_version_create(self):
        dataset = factories.Dataset()
        resource = factories.Resource(package_id = dataset['id'])
        user = factories.Sysadmin()

        version = resource_version_create(
            get_context(user),{
                'package_id': dataset['id'],
                'resource_id': resource['id'],
                'name': '1',
                'notes': 'Version notes'
            }
        )

        assert version
        assert version['package_id'] == dataset['id']
        assert version['resource_id'] == resource['id']
        assert version['notes'] == 'Version notes'
        assert version['name'] == '1'
        assert version['creator_user_id'] == user['id']

    def test_cannot_create_versions_with_same_name(self):
        dataset = factories.Dataset()
        resource = factories.Resource(package_id = dataset['id'])
        user = factories.Sysadmin()

        version = resource_version_create(
            get_context(user), {
                'package_id': dataset['id'],
                'resource_id': resource['id'],
                'name': '1',
                'notes': 'Version notes'
            }
        )

        with pytest.raises(toolkit.ValidationError):
            resource_version_create(
                get_context(user), {
                    'package_id': dataset['id'],
                    'resource_id': resource['id'],
                    'name': '1',
                    'notes': 'Version notes'
                }
            )

    def test_fails_if_objects_do_not_exist(self):
        user = factories.Sysadmin()
        with pytest.raises(toolkit.ObjectNotFound) as e:
            resource_version_create(
                get_context(user), {
                    'package_id': 'fake-dataset-id',
                    'resource_id': 'fake-resource-id',
                    'name': '1',
                    'notes': 'Version notes'
                }
            )
            assert e.msg == 'Dataset not found'

        dataset = factories.Dataset()
        with pytest.raises(toolkit.ObjectNotFound) as e:
            resource_version_create(
                get_context(user), {
                    'package_id': dataset['id'],
                    'resource_id': 'fake-resource-id',
                    'name': '1',
                    'notes': 'Version notes'
                }
            )
            assert e.msg == 'Resource not found'

    def test_fails_if_not_name_provided(self):
        dataset = factories.Dataset()
        resource = factories.Resource(package_id = dataset['id'])
        user = factories.Sysadmin()

        with pytest.raises(toolkit.ValidationError):
            resource_version_create(
                get_context(user), {
                    'package_id': dataset['id'],
                    'resource_id': resource['id'],
                    'notes': 'Version notes'
                }
            )

    def test_version_activity_is_correct(self):
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            name='First name'
            )
        user = factories.Sysadmin()
        context = get_context(user)

        version = resource_version_create(
            context, {
                'package_id': dataset['id'],
                'resource_id': resource['id'],
                'name': '1',
                'notes': 'Version notes'
            }
        )

        toolkit.get_action('resource_patch')(context, {
            'id': resource['id'], 'name': 'Second Name'
        })

        package = toolkit.get_action('activity_data_show')(
            context, {'id': version['activity_id']}
            )['package']
        activity_resource = package['resources'][0]

        assert activity_resource['id'] == resource['id']
        assert activity_resource['name'] == 'First name'

        version = resource_version_create(
            context, {
                'package_id': dataset['id'],
                'resource_id': resource['id'],
                'name': '2'
            }
        )

        package = toolkit.get_action('activity_data_show')(
            context, {'id': version['activity_id']}
            )['package']
        activity_resource = package['resources'][0]

        assert activity_resource['id'] == resource['id']
        assert activity_resource['name'] == 'Second Name'
