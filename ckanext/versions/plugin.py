# encoding: utf-8
import logging
from datetime import datetime

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.versions import cli
from ckanext.versions.logic import action, auth, helpers
from ckanext.versions.model import tables_exist

log = logging.getLogger(__name__)


class VersionsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IClick)
    plugins.implements(plugins.IResourceView)

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
            'version_show': action.version_show,
            'version_delete': action.version_delete
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'version_create': auth.version_create,
            'version_delete': auth.version_delete,
            'version_list': auth.version_list,
            'version_show': auth.version_show,
        }

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'url_for_version': helpers.url_for_version,
            'url_for_resource_version': helpers.url_for_resource_version,
            'dataset_version_has_link_resources': helpers.has_link_resources,
            'dataset_version_compare_pkg_dicts': helpers.compare_pkg_dicts,
        }

    # IResourceView

    def info(self):
        return {'name': 'versions_view',
                'title': 'Version history',
                'icon': 'table',
                'default_title': plugins.toolkit._('Version history'),
                'iframed': False}

    def can_view(self, data_dict):
        context = {'user': toolkit.c.user}
        resource = data_dict['resource']
        resource_id = resource.get('id')
        version_list =  action.resource_version_list(context, {'resource_id': resource_id})

        if not version_list:
            return False
        return True

    def setup_template_variables(self, context, data_dict):
        context = {'user': toolkit.c.user}
        resource = data_dict['resource']
        resource_id = resource.get('id')
        version_list =  action.resource_version_list(context, {'resource_id': resource_id})

        return {
            'versions': version_list,
            'resource': resource
            }

    def view_template(self, context, data_dict):
        return 'versions_view.html'

    def form_template(self, context, data_dict):
        return False
