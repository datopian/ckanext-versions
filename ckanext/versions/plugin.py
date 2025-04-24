import os
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.versions.logic import auth, action, validators
from ckanext.versions import helpers, views


class VersionsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions, inherit=True)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IValidators, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "versions")


    # IActions
    def get_actions(self):
        return {
            "package_version_create": action.package_version_create,
            "package_version_show": action.package_version_show,
            "package_version_update": action.package_version_update,
            "package_update": action.package_update,
            "package_version_list": action.package_version_list,
            "package_version_delete": action.package_version_delete,
        }

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            "package_version_create": auth.package_version_create,
            "package_version_show": auth.package_version_show,
            "package_version_update": auth.package_version_update,
            "package_version_list": auth.package_version_list,
            "package_version_delete": auth.package_version_delete,
        }

    # IValidators
    def get_validators(self):
        return {
            "package_version": validators.package_version,
        }
    
    # ITemplateHelpers
    def get_helpers(self):
        return {
            "get_package_version_list": helpers.get_package_version_list,
        }   


    # IBlueprints
    def get_blueprint(self):
        return [views.dataset_version]
    

