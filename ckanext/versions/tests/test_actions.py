import pytest
from ckan.plugins import toolkit
from ckan.tests import factories

from ckanext.versions.logic.action import (resource_version_create,
                                           resource_version_current,
                                           resource_version_list,
                                           version_delete, version_show)
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

    def test_resource_version_create_using_name(self):
        dataset = factories.Dataset()
        resource = factories.Resource(package_id = dataset['id'])
        user = factories.Sysadmin()

        version = resource_version_create(
            get_context(user),{
                'package_id': dataset['name'],
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


@pytest.mark.usefixtures("clean_db", "versions_setup")
class TestResourceVersionList(object):

    def test_resource_version_list(self):
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            name='First name'
            )
        user = factories.Sysadmin()
        context = get_context(user)

        resource_version_create(
            context, {
                'package_id': dataset['id'],
                'resource_id': resource['id'],
                'name': '1'
            }
        )

        toolkit.get_action('resource_patch')(context, {
            'id': resource['id'], 'name': 'Second name'
        })

        resource_version_create(
            context, {
                'package_id': dataset['id'],
                'resource_id': resource['id'],
                'name': '2',
                'notes': 'Notes for version 2'
            }
        )

        version_list = resource_version_list(context, {
            'resource_id': resource['id']}
            )

        assert len(version_list) == 2
        assert version_list[0]['name'] == '2'
        assert version_list[0]['notes'] == 'Notes for version 2'
        assert version_list[1]['name'] == '1'
        assert version_list[0]['activity_id'] != version_list[1]['activity_id']

    def test_list_fails_if_resource_does_not_exist(self):
        user = factories.Sysadmin()
        with pytest.raises(toolkit.ObjectNotFound) as e:
            resource_version_list(
                get_context(user), {'resource_id': 'fake-resource-id'}
            )
            assert e.msg == 'Resource not found'

    def test_resource_version_current(self):
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            name='First name'
            )
        user = factories.Sysadmin()
        context = get_context(user)

        resource_version_create(
            context, {
                'package_id': dataset['id'],
                'resource_id': resource['id'],
                'name': '1'
            }
        )

        toolkit.get_action('resource_patch')(context, {
            'id': resource['id'], 'name': 'Second name'
        })

        resource_version_create(
            context, {
                'package_id': dataset['id'],
                'resource_id': resource['id'],
                'name': '2',
                'notes': 'Notes for version 2'
            }
        )

        current_version = resource_version_current(context, {
            'resource_id': resource['id']}
            )

        assert current_version['name'] == '2'
        assert current_version['notes'] == 'Notes for version 2'


@pytest.mark.usefixtures("clean_db", "versions_setup")
class TestVersionShow(object):

    def test_version_show(self):
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

        result = version_show(context, {'version_id': version['id']})

        assert result['id'] == version['id']
        assert result['name'] == '1'
        assert result['notes'] == 'Version notes'
        assert result['creator_user_id'] == user['id']

@pytest.mark.usefixtures("clean_db", "versions_setup")
class TestVersionDelete(object):

    def test_version_delete(self):
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

        assert version

        version_delete(context, {'version_id': version['id']})

        with pytest.raises(toolkit.ObjectNotFound):
            version_show(context, {'version_id': version['id']})
