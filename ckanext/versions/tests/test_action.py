from ckan import model
from ckan.plugins import toolkit
from ckan.tests import factories, helpers
from nose.tools import assert_equals, assert_raises

from ckanext.versions.tests import FunctionalTestBase


class TestVersionsActions(FunctionalTestBase):
    """Test cases for logic actions
    """

    def _get_context(self, user):
        return {
            'model': model,
            'user': user['name'],
            'ignore_auth': False
        }

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

    def test_create(self):
        """Test basic dataset version creation
        """
        context = self._get_context(self.org_admin)
        version = helpers.call_action(
            'dataset_version_create',
            context,
            dataset=self.dataset['id'],
            name="Version 0.1.2",
            description="The best dataset ever, it **rules!**")

        assert_equals(version['package_id'], self.dataset['id'])
        assert_equals(version['package_revision_id'],
                      self.dataset['revision_id'])
        assert_equals(version['description'],
                      "The best dataset ever, it **rules!**")
        assert_equals(version['creator_user_id'], self.org_admin['id'])

    def test_create_name_already_exists(self):
        """Test that creating a version with an existing name for the same
        dataset raises an error
        """
        context = self._get_context(self.org_admin)
        helpers.call_action(
            'dataset_version_create',
            context,
            dataset=self.dataset['id'],
            name="HEAD",
            description="The best dataset ever, it **rules!**")

        assert_raises(toolkit.ValidationError, helpers.call_action,
                      'dataset_version_create', context,
                      dataset=self.dataset['id'],
                      name="HEAD",
                      description="This is also a good version")

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

    def test_list(self):
        context = self._get_context(self.org_admin)
        helpers.call_action(
            'dataset_version_create',
            context,
            dataset=self.dataset['id'],
            name="Version 0.1.2",
            description="The best dataset ever, it **rules!**")

        versions = helpers.call_action('dataset_version_list',
                                       context,
                                       dataset=self.dataset['id'])
        assert_equals(len(versions), 1)

    def test_list_no_versions(self):
        context = self._get_context(self.org_admin)
        versions = helpers.call_action('dataset_version_list',
                                       context,
                                       dataset=self.dataset['id'])
        assert_equals(len(versions), 0)

    def test_list_missing_dataset_id(self):
        payload = {}
        assert_raises(toolkit.ValidationError, helpers.call_action,
                      'dataset_version_list', **payload)

    def test_list_not_found(self):
        payload = {'dataset': 'abc123'}
        assert_raises(toolkit.ObjectNotFound, helpers.call_action,
                      'dataset_version_list', **payload)

    def test_create_two_versions_for_same_revision(self):
        context = self._get_context(self.org_admin)
        helpers.call_action(
            'dataset_version_create',
            context,
            dataset=self.dataset['id'],
            name="Version 0.1.2",
            description="The best dataset ever, it **rules!**")

        helpers.call_action(
            'dataset_version_create',
            context,
            dataset=self.dataset['id'],
            name="latest",
            description="This points to the latest version")

        versions = helpers.call_action('dataset_version_list',
                                       context,
                                       dataset=self.dataset['id'])
        assert_equals(len(versions), 2)

    def test_delete(self):
        context = self._get_context(self.org_admin)
        version = helpers.call_action(
            'dataset_version_create',
            context,
            dataset=self.dataset['id'],
            name="Version 0.1.2",
            description="The best dataset ever, it **rules!**")

        helpers.call_action('dataset_version_delete', context,
                            id=version['id'])

        versions = helpers.call_action('dataset_version_list',
                                       context,
                                       dataset=self.dataset['id'])
        assert_equals(len(versions), 0)

    def test_delete_not_found(self):
        payload = {'id': 'abc123'}
        assert_raises(toolkit.ObjectNotFound, helpers.call_action,
                      'dataset_version_delete', **payload)

    def test_delete_missing_param(self):
        payload = {}
        assert_raises(toolkit.ValidationError, helpers.call_action,
                      'dataset_version_delete', **payload)

    def test_show(self):
        context = self._get_context(self.org_admin)
        version1 = helpers.call_action(
            'dataset_version_create',
            context,
            dataset=self.dataset['id'],
            name="Version 0.1.2",
            description="The best dataset ever, it **rules!**")

        version2 = helpers.call_action('dataset_version_show', context,
                                       id=version1['id'])

        assert_equals(version2, version1)

    def test_show_not_found(self):
        payload = {'id': 'abc123'}
        assert_raises(toolkit.ObjectNotFound, helpers.call_action,
                      'dataset_version_show', **payload)

    def test_show_missing_param(self):
        payload = {}
        assert_raises(toolkit.ValidationError, helpers.call_action,
                      'dataset_version_show', **payload)

    def test_update_last_version(self):
        context = self._get_context(self.org_admin)
        version = helpers.call_action(
            'dataset_version_create',
            context,
            dataset=self.dataset['id'],
            name="Version 0.1.2",
            description="The best dataset ever, it **rules!**")

        updated_version = helpers.call_action(
            'dataset_version_update',
            context,
            dataset=self.dataset['id'],
            version=version['id'],
            name="Edited Version 0.1.2",
            description="Edited Description"
        )

        assert_equals(version['id'],
                      updated_version['id'])
        assert_equals(version['package_revision_id'],
                      updated_version['package_revision_id'])
        assert_equals(updated_version['description'],
                      "Edited Description")
        assert_equals(updated_version['name'],
                      "Edited Version 0.1.2")

    def test_update_old_version(self):
        context = self._get_context(self.org_admin)
        old_version = helpers.call_action(
            'dataset_version_create',
            context,
            dataset=self.dataset['id'],
            name="Version 1",
            description="This is an old version!")

        helpers.call_action(
            'dataset_version_create',
            context,
            dataset=self.dataset['id'],
            name="Version 2",
            description="This is a recent version!")

        updated_version = helpers.call_action(
            'dataset_version_update',
            context,
            dataset=self.dataset['id'],
            version=old_version['id'],
            name="Version 1.1",
            description="This is an edited old version!"
            )

        assert_equals(old_version['id'],
                      updated_version['id'])
        assert_equals(old_version['package_revision_id'],
                      updated_version['package_revision_id'])
        assert_equals(updated_version['description'],
                      "This is an edited old version!")
        assert_equals(updated_version['name'],
                      "Version 1.1")

    def test_update_not_existing_version_raises_error(self):
        context = self._get_context(self.org_admin)

        assert_raises(
            toolkit.ObjectNotFound, helpers.call_action,
            'dataset_version_update', context,
            dataset=self.dataset['id'],
            version='abc-123',
            name="Edited Version 0.1.2",
            description='Edited Description'
        )
