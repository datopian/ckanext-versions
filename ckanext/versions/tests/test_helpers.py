import mock
import pytest

from ckan.plugins import toolkit
from ckanext.versions import helpers
from ckanext.versions.helpers import dataset_version_for_activity_id
from ckanext.versions.tests import get_context


@pytest.mark.ckan_config('ckan.site_url', 'http://ckan:5000')
def test_version_download_url_without_filename():
    url = 'http://ckan:5000/dataset/<id>/resource/<resource_id>/download/'
    download_url = helpers.download_url(url, '<version_id>')

    assert download_url == 'http://ckan:5000/dataset/<id>/resource/<resource_id>/version/<version_id>/download/'


@pytest.mark.ckan_config('ckan.site_url', 'http://ckan:5000')
def test_version_download_url_with_filename():
    url = 'http://ckan:5000/dataset/<id>/resource/<resource_id>/download/filename.csv'
    download_url = helpers.download_url(url, '<version_id>')

    assert download_url == 'http://ckan:5000/dataset/<id>/resource/<resource_id>/version/<version_id>/download/filename.csv'


@pytest.mark.ckan_config('ckan.site_url', 'http://ckan:5000')
def test_version_download_url_with_external_url():
    url = 'https://www.my-external-url.com/external-filename.csv'
    download_url = helpers.download_url(url, '<version_id>')

    assert download_url == url


@pytest.mark.usefixtures('clean_db', 'versions_setup', 'with_request_context')
def test_dataset_version_for_activity_id_return_version(org_editor, test_dataset, test_version):
    activity_id = test_version['activity_id']

    with mock.patch('ckanext.versions.helpers.toolkit.g', user=org_editor['name']):
        actual_version = dataset_version_for_activity_id(test_dataset['id'], activity_id)
    assert test_version['id'] == actual_version['id']


@pytest.mark.usefixtures('clean_db', 'versions_setup', 'with_request_context')
def test_dataset_version_for_activity_returns_none_if_no_version(app, test_dataset, org_editor):
    context = get_context(org_editor)
    toolkit.get_action('package_patch')(
        context,
        {
            "id": test_dataset['id'],
            "name": "updated-name"
        }
    )
    activities = toolkit.get_action('package_activity_list')(
        context,
        {
            'id': test_dataset['id']
        }
    )
    activity_id = activities[0]['id']
    with mock.patch('ckanext.versions.helpers.toolkit.g', user=org_editor['name']):
        version = dataset_version_for_activity_id(test_dataset['id'], activity_id)
    assert None is version
