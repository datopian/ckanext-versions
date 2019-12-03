# encoding: utf-8

import logging

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.versions.logic import action, auth, helpers, uploader
from ckanext.versions.model import tables_exist
from ckanext.versions import blueprints

log = logging.getLogger(__name__)


class VersionsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.IUploader, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint)

    # IConfigurer

    def update_config(self, config_):
        if not tables_exist():
            log.critical(
                "The versions extension requires a database setup. Please run "
                "the following to create the database tables: \n"
                "paster --plugin=ckanext-versions versions init-db"
            )
        else:
            log.debug("Dataset versions tables verified to exist")

        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'versions')

    # IActions

    def get_actions(self):
        return {
            'dataset_version_create': action.dataset_version_create,
            'dataset_version_delete': action.dataset_version_delete,
            'dataset_version_list': action.dataset_version_list,
            'dataset_version_update': action.dataset_version_update,
            'dataset_version_show': action.dataset_version_show,
            'dataset_version_promote': action.dataset_version_promote,
            'package_show_version': action.package_show_version,
            'resource_show_version': action.resource_show_version,
            'dataset_versions_diff': action.dataset_versions_diff,

            # Overridden
            'package_show': action.package_show_revision,
            'resource_show': action.resource_show_revision
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'dataset_version_create': auth.dataset_version_create,
            'dataset_version_delete': auth.dataset_version_delete,
            'dataset_version_list': auth.dataset_version_list,
            'dataset_version_show': auth.dataset_version_show,
            'dataset_versions_diff': action.dataset_versions_diff,
        }

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'dataset_version_show_url': helpers.get_show_url,
            'dataset_version_resource_show_url': helpers.get_resource_show_url,
            'dataset_version_get_show_url': helpers.get_show_url,
            'dataset_version_has_link_resources': helpers.has_link_resources,
            'dataset_version_compare_pkg_dicts': helpers.compare_pkg_dicts,
        }

    # IPackageController

    def before_view(self, pkg_dict):
        versions = action.dataset_version_list({"ignore_auth": True},
                                               {"dataset": pkg_dict['id']})
        pkg_dict.update({'versions': versions})

        version_id = toolkit.request.params.get('version', None)
        if version_id:
            version = action.dataset_version_show({"ignore_auth": True},
                                                  {"id": version_id})
            toolkit.c.current_version = version

            # Hide package creation / update date if viewing a specific version
            pkg_dict['metadata_created'] = None
            pkg_dict['metadata_updated'] = None

        return pkg_dict

    # IBlueprint

    def get_blueprint(self):
        return [blueprints.versions]

    # IResourceController

    def before_delete(self, context, resource, resources):
        pass

    # IUploader

    def get_resource_uploader(self, data_dict):
        return uploader.get_uploader(self, data_dict)
