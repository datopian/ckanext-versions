import pytest
from ckan.plugins import toolkit
from ckan.tests import factories, helpers

from ckanext.versions.logic.action import (
    activity_resource_show, get_activity_id_from_resource_version_name,
    resource_has_versions, resource_has_versions, resource_in_activity,
    resource_version_create, resource_version_current,
    resource_version_list, version_delete, version_show)
from ckanext.versions.tests import get_context


@pytest.mark.usefixtures('clean_db', 'versions_setup')
class TestCreateResourceVersion(object):

    def test_resource_version_create(self):
        dataset = factories.Dataset()
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.Sysadmin()

        version = resource_version_create(
            get_context(user), {
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

    def test_resource_version_create_editor_user(self):
        user = factories.User()
        owner_org = factories.Organization(
            users=[{'name': user['name'], 'capacity': 'editor'}]
        )
        dataset = factories.Dataset(owner_org=owner_org['id'])
        resource = factories.Resource(package_id=dataset['id'])

        version = resource_version_create(
            get_context(user), {
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
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.Sysadmin()

        resource_version_create(
            get_context(user), {
                'resource_id': resource['id'],
                'name': '1',
                'notes': 'Version notes'
            }
        )

        with pytest.raises(toolkit.ValidationError):
            resource_version_create(
                get_context(user), {
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
                    'resource_id': 'fake-resource-id',
                    'name': '1',
                    'notes': 'Version notes'
                }
            )
            assert e.msg == 'Dataset not found'

        factories.Dataset()
        with pytest.raises(toolkit.ObjectNotFound) as e:
            resource_version_create(
                get_context(user), {
                    'resource_id': 'fake-resource-id',
                    'name': '1',
                    'notes': 'Version notes'
                }
            )
            assert e.msg == 'Resource not found'

    def test_fails_if_not_name_provided(self):
        dataset = factories.Dataset()
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.Sysadmin()

        with pytest.raises(toolkit.ValidationError):
            resource_version_create(
                get_context(user), {
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

    def test_resource_has_version(self):
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            name='First name'
            )
        user = factories.Sysadmin()
        context = get_context(user)

        assert False == resource_has_versions(
            context, {'resource_id': resource['id']}
            )

        resource_version_create(
            context, {
                'resource_id': resource['id'],
                'name': '1',
                'notes': 'Version notes'
            }
        )

        assert True == resource_has_versions(
            context, {'resource_id': resource['id']}
            )

    def test_resource_version_create_creator_user_id_parameter(self):
        user = factories.User()
        owner_org = factories.Organization(
            users=[{'name': user['name'], 'capacity': 'editor'}]
        )
        user_creator = factories.User()
        dataset = factories.Dataset(owner_org=owner_org['id'])
        resource = factories.Resource(package_id=dataset['id'])

        version = resource_version_create(
            get_context(user), {
                'resource_id': resource['id'],
                'name': '1',
                'notes': 'Version notes',
                'creator_user_id': user_creator['id']
            }
        )

        assert version
        assert version['package_id'] == dataset['id']
        assert version['resource_id'] == resource['id']
        assert version['notes'] == 'Version notes'
        assert version['name'] == '1'
        assert version['creator_user_id'] == user_creator['id']


@pytest.mark.usefixtures('clean_db', 'versions_setup')
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
                'resource_id': resource['id'],
                'name': '1'
            }
        )

        toolkit.get_action('resource_patch')(context, {
            'id': resource['id'], 'name': 'Second name'
        })

        resource_version_create(
            context, {
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
                'resource_id': resource['id'],
                'name': '1'
            }
        )

        toolkit.get_action('resource_patch')(context, {
            'id': resource['id'], 'name': 'Second name'
        })

        resource_version_create(
            context, {
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


@pytest.mark.usefixtures('clean_db', 'versions_setup')
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

    def test_version_show_for_version_name(self):
        dataset = factories.Dataset()
        resource = factories.Resource(
            package_id=dataset['id'],
            name='First name'
        )
        user = factories.Sysadmin()
        context = get_context(user)

        version = resource_version_create(
            context, {
                'resource_id': resource['id'],
                'name': '1',
                'notes': 'Version notes'
            }
        )

        result = version_show(
            context,
            {'version_id': version['name'],
             'dataset_id': dataset['id']}
        )

        assert result['id'] == version['id']
        assert result['name'] == '1'
        assert result['notes'] == 'Version notes'
        assert result['creator_user_id'] == user['id']


@pytest.mark.usefixtures('clean_db', 'versions_setup')
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
                'resource_id': resource['id'],
                'name': '1',
                'notes': 'Version notes'
            }
        )

        assert version

        version_delete(context, {'version_id': version['id']})

        with pytest.raises(toolkit.ObjectNotFound):
            version_show(context, {'version_id': version['id']})


@pytest.mark.usefixtures('clean_db', 'versions_setup')
class TestActivityActions(object):

    def test_activity_resource_shows_correct_resource(self):
        user = factories.User()
        owner_org = factories.Organization(
            users=[{'name': user['name'], 'capacity': 'editor'}]
        )
        dataset = factories.Dataset(owner_org=owner_org['id'])
        resource = factories.Resource(
            package_id=dataset['id'],
            name='First name'
            )

        context = get_context(user)

        version = resource_version_create(
            context, {
                'resource_id': resource['id'],
                'name': '1',
                'notes': 'Version notes'
            }
        )

        toolkit.get_action('resource_patch')(context, {
            'id': resource['id'], 'name': 'Second name'
        })

        version_2 = resource_version_create(
            context, {
                'resource_id': resource['id'],
                'name': '2',
                'notes': 'Notes for version 2'
            }
        )

        activity_resource = activity_resource_show(
            context, {
                'activity_id': version['activity_id'],
                'resource_id': resource['id']
            }
        )

        assert activity_resource
        assert activity_resource['name'] == 'First name'

        activity_resource_2 = activity_resource_show(
            context, {
                'activity_id': version_2['activity_id'],
                'resource_id': resource['id']
            }
        )

        assert activity_resource_2
        assert activity_resource_2['name'] == 'Second name'

    def test_get_activity_id_from_resource_version_name(self):
        user = factories.User()
        owner_org = factories.Organization(
            users=[{'name': user['name'], 'capacity': 'editor'}]
        )
        dataset = factories.Dataset(owner_org=owner_org['id'])
        resource = factories.Resource(
            package_id=dataset['id'],
            name='First name'
            )

        context = get_context(user)

        version = resource_version_create(
            context, {
                'resource_id': resource['id'],
                'name': '1',
                'notes': 'Version notes'
            }
        )
        expected_activity_id = version['activity_id']

        activity_id = get_activity_id_from_resource_version_name(
            context,
            {'resource_id': resource['id'], 'version_name': version['name']}
        )

        assert expected_activity_id == activity_id

    def test_resource_in_activity(self):
        user = factories.User()
        owner_org = factories.Organization(
            users=[{'name': user['name'], 'capacity': 'editor'}]
        )
        dataset = factories.Dataset(owner_org=owner_org['id'])
        resource = factories.Resource(
            package_id=dataset['id'],
            name='Resource 1'
            )

        context = get_context(user)

        version = resource_version_create(
            context, {
                'resource_id': resource['id'],
                'name': '1',
                'notes': 'Version notes'
            }
        )
        expected_activity_id = version['activity_id']

        assert True == resource_in_activity(context, {
            'activity_id': expected_activity_id,
            'resource_id': resource['id']}
            )

        resource_2 = factories.Resource(
            package_id=dataset['id'],
            name='Resource 2'
            )

        assert False == resource_in_activity(context, {
            'activity_id': expected_activity_id,
            'resource_id': resource_2['id']}
            )


@pytest.mark.usefixtures('clean_db', 'versions_setup')
class TestResourceView(object):
    def test_resource_view_list_returns_versions_view_last(self):
        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org['id'])
        resource = factories.Resource(
            package_id=dataset['id']
        )
        image_view_dict = {
            'resource_id': resource['id'],
            'view_type': 'image_view',
            'title': 'Image View',
            'description': 'A nice image view',
            'image_url': 'url',
        }

        versions_view_dict = {
            'resource_id': resource['id'],
            'view_type': 'versions_view',
            'title': 'Versions View',
            'description': 'A nice versions view',
        }

        versions_view = helpers.call_action('resource_view_create', **versions_view_dict)
        image_view = helpers.call_action('resource_view_create', **image_view_dict)

        resource_views = helpers.call_action('resource_view_list', id=resource['id'])

        assert resource_views[0]['id'] == image_view['id']
        assert resource_views[1]['id'] == versions_view['id']

    def test_resource_view_list_returns_default_order_if_no_versions_view(self):
        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org['id'])
        resource = factories.Resource(
            package_id=dataset['id']
        )
        image_view_dict = {
            'resource_id': resource['id'],
            'view_type': 'image_view',
            'title': 'Image View',
            'description': 'A nice image view',
            'image_url': 'url',
        }

        image_view_dict_2 = {
            'resource_id': resource['id'],
            'view_type': 'image_view',
            'title': 'Image View 2',
            'image_url': 'url',
        }

        image_view = helpers.call_action('resource_view_create', **image_view_dict)
        image_view_2 = helpers.call_action('resource_view_create', **image_view_dict_2)

        resource_views = helpers.call_action('resource_view_list', id=resource['id'])

        assert resource_views[0]['id'] == image_view['id']
        assert resource_views[1]['id'] == image_view_2['id']
