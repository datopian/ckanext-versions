import pytest

from ckanext.versions.model import create_tables, tables_exist


@pytest.fixture
def versions_setup():
    if not tables_exist():
        create_tables()
