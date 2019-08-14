from ckan.tests import helpers

from ckanext.versions.model import create_tables, tables_exist


class FunctionalTestBase(helpers.FunctionalTestBase):

    @classmethod
    def setup_class(cls):

        super(FunctionalTestBase, cls).setup_class()

        if not tables_exist():
            create_tables()
