from ckan.tests import helpers

from ckanext.versions import model


class FunctionalTestBase(helpers.FunctionalTestBase):

    _load_plugins = ['versions']

    def setup(self):
        if not model.tables_exist():
            model.create_tables()
        super(FunctionalTestBase, self).setup()
