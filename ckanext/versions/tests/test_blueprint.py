import pytest
from ckan.plugins import toolkit
from ckan.tests import factories, helpers

from ckanext.versions.logic.action import (
    activity_resource_show,
    get_activity_id_from_resource_version_name,
    resource_has_versions,
    resource_in_activity,
    resource_version_create,
    resource_version_current,
    resource_version_list,
    version_delete,
    version_show,
    resource_version_clear,
)
from ckanext.versions.tests import get_context


@pytest.mark.usefixtures("clean_db", "versions_setup")
def test_download_url_preserves_params(app):
    org = factories.Organization()
    dataset = factories.Dataset(owner_org=org["id"])
    resource = factories.Resource(package_id=dataset["id"])
    user = factories.Sysadmin()

    version = resource_version_create(
        get_context(user),
        {"resource_id": resource["id"], "name": "1", "notes": "Version notes"},
    )

    download_url = toolkit.url_for(
        "versions.version_download",
        id=dataset["id"],
        resource_id=resource["id"],
        version_id=version["id"],
        sensitive=True,  # Custom param
    )

    assert "sensitive=True" in download_url

    resp = app.get(download_url, follow_redirects=False)

    assert "sensitive=True" in resp.headers["Location"]
