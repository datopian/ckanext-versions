import os
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.versions.logic import auth, action
from ckan.lib.uploader import ResourceUpload as DefaultResourceUpload


class VersionsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    # plugins.implements(plugins.IUploader, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    
    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "versions")

    def get_resource_uploader(self, data_dict):
        return ResourceUpload(data_dict)
    
    # IActions
    def get_actions(self):
        return {
            'package_version_create': action.package_version_create

        }

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'package_version_create': auth.package_version_create
        }
    

class ResourceUpload(DefaultResourceUpload):
    path_prefix = 'filename_prefix_'

    def get_path(self, id: str):
        directory = self.get_directory(id)
        filepath = os.path.join(
            directory, '{}_{}'.format(self.path_prefix, id[6:]))
        return filepath
