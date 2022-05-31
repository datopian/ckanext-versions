import pytest

from ckan.plugins import toolkit, plugin_loaded, load as load_plugin, unload as unload_plugin
from ckanext.versions.model import create_tables, tables_exist


@pytest.fixture
def versions_setup():
    if not tables_exist():
        create_tables()


@pytest.fixture
def load_activity_plugin():
    if toolkit.check_ckan_version(min_version="2.10"):
        if not plugin_loaded("activity"):
            load_plugin("activity")
        yield
        if plugin_loaded("activity"):
            unload_plugin("activity")
