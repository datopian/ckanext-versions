# encoding: utf-8
import logging
from datetime import datetime

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.uploader import ALLOWED_UPLOAD_TYPES

from ckanext.versions.logic import action, auth, helpers, uploader
from ckanext.versions.model import tables_exist

UPLOAD_TS_FIELD = uploader.UPLOAD_TS_FIELD

log = logging.getLogger(__name__)


class VersionsPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.IUploader, inherit=True)
    plugins.implements(plugins.IDatasetForm, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)

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
            'package_show_version': action.package_show_version,
            'resource_show_version': action.resource_show_version,

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
        }

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'url_for_version': helpers.url_for_version,
            'url_for_resource_version': helpers.url_for_resource_version,
            'dataset_version_has_link_resources': helpers.has_link_resources,
        }

    # IPackageController

    def before_view(self, pkg_dict):
        try:
            versions = action.dataset_version_list({"ignore_auth": True},
                                                   {"dataset": pkg_dict['id']})
        except toolkit.ObjectNotFound:
            # Do not blow up if package is gone
            return pkg_dict

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
        return True

    def package_types(self):
        return []

    # IResourceController

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
        elif current is not None:
            data_dict[UPLOAD_TS_FIELD] = current.get(UPLOAD_TS_FIELD, None)
        return data_dict
