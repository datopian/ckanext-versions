from ckan.plugins import toolkit
from ckan.tests import factories, helpers
from nose.tools import assert_equals, assert_raises

from ckanext.versions.tests import FunctionalTestBase


class TestVersionsActions(FunctionalTestBase):
    """Test cases for logic actions
    """

    def setup(self):

        super(TestVersionsActions, self).setup()

        self.org_admin = factories.User()
        self.org_admin_name = self.org_admin['name'].encode('ascii')

        self.org_member = factories.User()
        self.org_member_name = self.org_member['name'].encode('ascii')

        self.org = factories.Organization(
            users=[
                {'name': self.org_member['name'], 'capacity': 'member'},
                {'name': self.org_admin['name'], 'capacity': 'admin'},
            ]
        )

        self.dataset = factories.Dataset()

    def test_list(self):
        versions = helpers.call_action('dataset_version_list',
                                       package_id=self.dataset['id'])
        assert_equals(len(versions), 1)

    def test_create(self):
        """Test basic dataset version creation
        """
        version = helpers.call_action(
            'dataset_version_create',
            dataset=self.dataset['id'],
            name="Version 0.1.2",
            description="The best dataset ever, it **rules!**")

        assert_equals(version['package_id'], self.dataset['id'])
        assert_equals(version['package_revision_id'],
                      self.dataset['revision_id'])
        assert_equals(version['description'],
                      "The best dataset ever, it **rules!**")

    def test_create_dataset_not_found(self):
        payload = {'dataset': 'abc123',
                   'name': "Version 0.1.2"}

        assert_raises(toolkit.ObjectNotFound, helpers.call_action,
                      'dataset_version_create', **payload)

    def test_create_missing_name(self):
        payload = {'dataset': self.dataset['id'],
                   'description': "The best dataset ever, it **rules!**"}

        assert_raises(toolkit.ValidationError, helpers.call_action,
                      'dataset_version_create', **payload)
