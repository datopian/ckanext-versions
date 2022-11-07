# encoding: utf-8
import logging

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.versions import cli, helpers
from ckanext.versions.blueprints import blueprint
from ckanext.versions.logic import action, auth
from ckanext.versions.model import tables_exist

log = logging.getLogger(__name__)


class VersionsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IResourceView)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint)

    # IClick

    def get_commands(self):
        return cli.get_commands()

    # IConfigurer

    def update_config(self, config_):
        if not tables_exist():
            log.critical(
                "The versions extension requires a database setup. Please run "
                "the following to create the database tables: \n"
                "ckan versions initdb"
            )
        else:
            log.debug("Dataset versions tables verified to exist")

        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'versions')

    # IActions

    def get_actions(self):
        return {
            'resource_version_create': action.resource_version_create,
            'resource_version_list': action.resource_version_list,
            'resource_version_current': action.resource_version_current,
            'resource_version_clear': action.resource_version_clear,
            'resource_version_update': action.resource_version_update,
            'version_show': action.version_show,
            'version_delete': action.version_delete,
            'resource_view_list': action.resource_view_list,
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'version_create': auth.version_create,
            'version_delete': auth.version_delete,
            'version_list': auth.version_list,
            'version_show': auth.version_show,
            'resource_version_clear': action.resource_version_clear,
        }

    # ITemplateHelpers

    def get_helpers(self):
        helper_functions = {
            'versions_resources_list_with_current_version': helpers.resources_list_with_current_version,
            'versions_resource_version_list': helpers.resource_version_list,
            'versions_resource_version_from_activity_id': helpers.resource_version_from_activity_id,
            'versions_resource_version_current': helpers.resource_version_current,
            'versions_download_url': helpers.download_url,
        }
        return helper_functions

    # IBlueprints
    def get_blueprint(self):
        return blueprint

    # IResourceView

    def info(self):
        return {'name': 'versions_view',
                'title': 'Version history',
                'icon': 'history',
                'default_title': plugins.toolkit._('Version history'),
                'iframed': False}

    def can_view(self, data_dict):
        context = {'ignore_auth': True}
        resource = data_dict['resource']
        resource_id = resource.get('id')

        return action.resource_has_versions(context, {'resource_id': resource_id})

    def setup_template_variables(self, context, data_dict):
        context = {'user': toolkit.c.user}
        resource = data_dict['resource']
        resource_id = resource.get('id')
        resource_history = action.resource_history(context, {
            'resource_id': resource_id}
            )
        return {
            'resource_history': resource_history
            }

    def view_template(self, context, data_dict):
        return 'versions/versions_view.html'

    def form_template(self, context, data_dict):
        return False
