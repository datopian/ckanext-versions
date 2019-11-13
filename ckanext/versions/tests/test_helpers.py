from ckan.tests import factories
from nose.tools import assert_equals

from ckanext.versions.logic import helpers
from ckanext.versions.tests import FunctionalTestBase


class TestHelpers(FunctionalTestBase):

    def setup(self):
        super(TestHelpers, self).setup()

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

        assert_equals(
            helpers.has_link_resources(self.dataset),
            True)

    def test_dataset_does_not_has_link_resources(self):
        upload_resource = factories.Resource(
            package_id=self.dataset['id'],
            url_type='upload'
        )

        self.dataset['resources'].append(upload_resource)

        assert_equals(
            helpers.has_link_resources(self.dataset),
            False)
