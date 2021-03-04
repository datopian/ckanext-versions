import pytest

from ckan.tests import factories

from ckanext.versions.logic import helpers


@pytest.mark.usefixtures("clean_db", "versions_setup")
class TestHelpers(object):

    def setup(self):
        #TODO: Refactor to a new pytest approach
        self.admin_user = factories.Sysadmin()

        self.org = factories.Organization(
            users=[
                {'name': self.admin_user['name'], 'capacity': 'admin'},
            ]
        )
        self.dataset = factories.Dataset(owner_org=self.org['id'],
                                         private=False)

    def test_dataset_has_link_resources(self):
        upload_resource = factories.Resource(
            package_id=self.dataset['id'],
            url_type='upload'
        )
        link_resource = factories.Resource(
            package_id=self.dataset['id'],
            url_type=''
        )

        self.dataset['resources'].extend([upload_resource, link_resource])

        assert helpers.has_link_resources(self.dataset) == True

    def test_dataset_does_not_has_link_resources(self):
        upload_resource = factories.Resource(
            package_id=self.dataset['id'],
            url_type='upload'
        )

        self.dataset['resources'].append(upload_resource)

        assert helpers.has_link_resources(self.dataset) == False
