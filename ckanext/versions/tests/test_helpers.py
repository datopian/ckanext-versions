import pytest

from ckanext.versions import helpers

@pytest.mark.ckan_config('ckan.site_url', 'http://ckan:5000')
def test_version_download_url_without_filename():
    url = 'http://ckan:5000/dataset/<id>/resource/<resource_id>/download/'
    download_url = helpers.download_url(url, 'v1.0')

    assert download_url == 'http://ckan:5000/dataset/<id>/resource/<resource_id>/v/v1.0/download/'


@pytest.mark.ckan_config('ckan.site_url', 'http://ckan:5000')
def test_version_download_url_with_filename():
    url = 'http://ckan:5000/dataset/<id>/resource/<resource_id>/download/filename.csv'
    download_url = helpers.download_url(url, 'v1.0')

    assert download_url == 'http://ckan:5000/dataset/<id>/resource/<resource_id>/v/v1.0/download/filename.csv'


@pytest.mark.ckan_config('ckan.site_url', 'http://ckan:5000')
def test_version_download_url_with_external_url():
    url = 'https://www.my-external-url.com/external-filename.csv'
    download_url = helpers.download_url(url, 'v1.0')

    assert download_url == url
