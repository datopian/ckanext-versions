from ckan import model
from ckan.plugins import toolkit
from ckan.tests import factories, helpers
from nose.tools import assert_raises
from parameterized import parameterized

from ckanext.versions.tests import FunctionalTestBase


class TestVersionsAuth(FunctionalTestBase):

    def _get_context(self, user):
        return {
            'model': model,
            'user': user if isinstance(user, basestring) else user['name']
        }

    def setup(self):

        super(TestVersionsAuth, self).setup()

        self.org_admin = factories.User()
        self.org_editor = factories.User()
        self.org_member = factories.User()
        self.other_org_admin = factories.User()
        self.admin_user = factories.Sysadmin()

        self.org = factories.Organization(
            users=[
                {'name': self.org_admin['name'], 'capacity': 'admin'},
                {'name': self.org_editor['name'], 'capacity': 'editor'},
                {'name': self.org_member['name'], 'capacity': 'member'},
            ]
        )

        self.other_org = factories.Organization(
            users=[
                {'name': self.other_org_admin['name'], 'capacity': 'admin'},
            ]
        )

        self.private_dataset = factories.Dataset(owner_org=self.org['id'],
                                                 private=True)
        self.public_dataset = factories.Dataset(owner_org=self.org['id'],
                                                private=False)

    @parameterized([
        ('org_admin', 'private_dataset'),
        ('org_admin', 'public_dataset'),
        ('org_editor', 'private_dataset'),
        ('org_editor', 'public_dataset'),
        ('admin_user', 'private_dataset'),
        ('admin_user', 'public_dataset'),
    ])
    def test_create_is_authorized(self, user_type, dataset_type):
        """Test that authorized users can create versions on a given dataset
        """
        user = getattr(self, user_type)
        dataset = getattr(self, dataset_type)
        context = self._get_context(user)
        assert helpers.call_auth('version_create',
                                 context=context,
                                 dataset=dataset['id'])

    @parameterized([
        ('org_member', 'private_dataset'),
        ('org_member', 'public_dataset'),
        ('other_org_admin', 'private_dataset'),
        ('other_org_admin', 'public_dataset'),
    ])
    def test_create_is_unauthorized(self, user_type, dataset_type):
        """Test that unauthorized users cannot create versions on a given
        dataset
        """
        user = getattr(self, user_type)
        dataset = getattr(self, dataset_type)
        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized,
                      helpers.call_auth,
                      'version_create',
                      context=context,
                      dataset=dataset['id'])

    @parameterized([
        ('org_admin', 'private_dataset'),
        ('org_admin', 'public_dataset'),
        ('org_editor', 'private_dataset'),
        ('org_editor', 'public_dataset'),
        ('admin_user', 'private_dataset'),
        ('admin_user', 'public_dataset'),
    ])
    def test_delete_is_authorized(self, user_type, dataset_type):
        """Test that authorized users can delete versions on a given dataset
        """
        user = getattr(self, user_type)
        dataset = getattr(self, dataset_type)
        context = self._get_context(user)
        assert helpers.call_auth('dataset_version_delete',
                                 context=context,
                                 dataset=dataset['id'])

    @parameterized([
        ('org_member', 'private_dataset'),
        ('org_member', 'public_dataset'),
        ('other_org_admin', 'private_dataset'),
        ('other_org_admin', 'public_dataset'),
    ])
    def test_delete_is_unauthorized(self, user_type, dataset_type):
        """Test that unauthorized users cannot delete versions on a given
        dataset
        """
        user = getattr(self, user_type)
        dataset = getattr(self, dataset_type)
        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized,
                      helpers.call_auth,
                      'version_delete',
                      context=context,
                      dataset=dataset['id'])

    @parameterized([
        ('org_admin', 'private_dataset'),
        ('org_admin', 'public_dataset'),
        ('org_editor', 'private_dataset'),
        ('org_editor', 'public_dataset'),
        ('org_member', 'private_dataset'),
        ('org_member', 'public_dataset'),
        ('admin_user', 'private_dataset'),
        ('admin_user', 'public_dataset'),
        ('other_org_admin', 'public_dataset'),
    ])
    def test_list_is_authorized(self, user_type, dataset_type):
        """Test that authorized users can list versions of a given dataset
        """
        user = getattr(self, user_type)
        dataset = getattr(self, dataset_type)
        context = self._get_context(user)
        assert helpers.call_auth('version_list',
                                 context=context,
                                 dataset=dataset['id'])

    @parameterized([
        ('other_org_admin', 'private_dataset'),
    ])
    def test_list_is_unauthorized(self, user_type, dataset_type):
        """Test that unauthorized users cannot list versions on a given
        dataset
        """
        user = getattr(self, user_type)
        dataset = getattr(self, dataset_type)
        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized,
                      helpers.call_auth,
                      'dataset_version_list',
                      context=context,
                      dataset=dataset['id'])

    @parameterized([
        ('org_admin', 'private_dataset'),
        ('org_admin', 'public_dataset'),
        ('org_editor', 'private_dataset'),
        ('org_editor', 'public_dataset'),
        ('org_member', 'private_dataset'),
        ('org_member', 'public_dataset'),
        ('admin_user', 'private_dataset'),
        ('admin_user', 'public_dataset'),
        ('other_org_admin', 'public_dataset'),
    ])
    def test_show_is_authorized(self, user_type, dataset_type):
        """Test that authorized users can view versions of a given dataset
        """
        user = getattr(self, user_type)
        dataset = getattr(self, dataset_type)
        context = self._get_context(user)
        assert helpers.call_auth('version_show',
                                 context=context,
                                 dataset=dataset['id'])

    @parameterized([
        ('other_org_admin', 'private_dataset'),
    ])
    def test_show_is_unauthorized(self, user_type, dataset_type):
        """Test that unauthorized users cannot view versions on a given
        dataset
        """
        user = getattr(self, user_type)
        dataset = getattr(self, dataset_type)
        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized,
                      helpers.call_auth,
                      'version_show',
                      context=context,
                      dataset=dataset['id'])
