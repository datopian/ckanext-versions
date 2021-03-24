import pytest
from ckan import model
from ckan.plugins import toolkit
from ckan.tests import factories

from ckanext.versions.logic.action import resource_version_create


@pytest.mark.usefixtures("clean_db", "versions_setup")
class TestCreateResourceVersion(object):

    def _get_context(self, user):
        return {
            'model': model,
            'user': user if isinstance(user, str) else user['name']
        }

    def test_resource_version_create(self):
        dataset = factories.Dataset()
        resource = factories.Resource(package_id = dataset['id'])
        user = factories.Sysadmin()

        version = resource_version_create(
            self._get_context(user),{
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
            self._get_context(user),{
                'package_id': dataset['id'],
                'resource_id': resource['id'],
                'name': '1',
                'notes': 'Version notes'
            }
        )

        with pytest.raises(toolkit.ValidationError):
            resource_version_create(
                self._get_context(user),{
                    'package_id': dataset['id'],
                    'resource_id': resource['id'],
                    'name': '1',
                    'notes': 'Version notes'
                }
            )
