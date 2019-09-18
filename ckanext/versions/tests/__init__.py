from ckan.tests import helpers

from ckanext.versions import model


class FunctionalTestBase(helpers.FunctionalTestBase):

    _load_plugins = ['versions']

    @classmethod
    def setup_class(cls):
        super(FunctionalTestBase, cls).setup_class()
        if not model.tables_exist():
            model.create_tables()
