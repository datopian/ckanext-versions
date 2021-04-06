# encoding: utf-8
import logging
from datetime import datetime

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.uploader import ALLOWED_UPLOAD_TYPES

from ckanext.versions import cli
from ckanext.versions.logic import action, auth, helpers, uploader
from ckanext.versions.model import tables_exist

from ckan.lib.helpers import resource_display_name

UPLOAD_TS_FIELD = uploader.UPLOAD_TS_FIELD

log = logging.getLogger(__name__)


class VersionsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.IUploader, inherit=True)
    plugins.implements(plugins.IDatasetForm, inherit=True)
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
            'format_date': helpers.format_date,
            'get_version_list': helpers.get_version_list,
        }

    # IUploader

    def get_resource_uploader(self, data_dict):
        return uploader.get_uploader(self, data_dict)

    # IDatasetForm

    def update_package_schema(self):
        schema = super(VersionsPlugin, self).update_package_schema()
        schema['resources'].update(
            {UPLOAD_TS_FIELD: [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras')
            ]}
        )
        return schema

    def show_package_schema(self):
        schema = super(VersionsPlugin, self).show_package_schema()
        schema['resources'].update(
            {UPLOAD_TS_FIELD: [
                toolkit.get_converter('convert_from_extras'),
                toolkit.get_validator('ignore_missing')
            ]}
        )
        return schema

    def is_fallback(self):
        return False

    def package_types(self):
        return []

    # IResourceController

    def before_delete(self, context, resource, resources):
        pass

    def before_create(self, context, data_dict):
        return self._set_upload_timestamp(data_dict)

    def before_update(self, context, current, data_dict):
        return self._set_upload_timestamp(data_dict, current)

    def _set_upload_timestamp(self, data_dict, current=None):
        """When creating or updating a resource, if it contains a file upload,
        save the upload timestamp as a resource extra field
        """
        if isinstance(data_dict.get('upload'), ALLOWED_UPLOAD_TYPES):
            ts = datetime.now().isoformat()
            log.debug("Setting upload timestamp to %s=%s", UPLOAD_TS_FIELD, ts)
            data_dict[UPLOAD_TS_FIELD] = ts
        elif data_dict.get('clear_upload') and UPLOAD_TS_FIELD in data_dict:
            log.debug("Clearing upload timestamp field")
            del data_dict[UPLOAD_TS_FIELD]
        elif current and UPLOAD_TS_FIELD in current:
            data_dict[UPLOAD_TS_FIELD] = current[UPLOAD_TS_FIELD]
        return data_dict

    #IResourceView
    def info(self):
            return {'name': 'versions_view',
                    'title': 'Versioning',
                    'icon': 'table',
                    'default_title': plugins.toolkit._('Versioning'),}

    def can_view(self, data_dict):
        context = {'user': toolkit.c.user}

        version_list = helpers.get_version_list(context, data_dict)

        if not version_list:
            return False
        return True

    def setup_template_variables(self,context, data_dict):
        version_list = helpers.get_version_list(context, data_dict)
        resource_name = resource_display_name(data_dict['resource'])

        return {
            'resource_version': version_list,
            'resource_name': resource_name
            }

    def view_template(self, context, data_dict):
        return 'versions_view.html'

    def form_template(self, context, data_dict):
        return False
