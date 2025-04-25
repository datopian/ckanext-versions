import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.versions.logic import auth, action, validators
from ckanext.versions import helpers, views
from ckanext.versions.uploader import (
    _get_stringified_date,
    LocalResourceUpload,
    S3ResourceUpload,
)


class VersionsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions, inherit=True)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IValidators, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IUploader, inherit=True)
    plugins.implements(plugins.IResourceController, inherit=True)

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
            "package_version_exists": action.package_version_exists,
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

    # IUploader
    def get_resource_uploader(self, data_dict):
        ## check if s3filestore is installed then use S3ResourceUpload
        ## otherwise fallback to LocalResourceUpload
        if "s3filestore" in toolkit.config.get("ckan.plugins", ""):
            return S3ResourceUpload(data_dict)
        else:
            return LocalResourceUpload(data_dict)

    # IResourceController
    def before_resource_show(self, resource, **kwargs):
        # This method is called before the resource
        url = resource["url"]
        if resource.get("url_type") == "upload":
            # update the resource URL to include the last modified date
            # in the format YYYY-MM-DD-HH-MM-SS
            url_parts = url.rsplit("/")
            if "download" in url_parts:
                index = url_parts.index("download")
                last_modified = resource.get("last_modified")
                last_modified_str = _get_stringified_date(last_modified)
                if index + 1 >= len(url_parts) or not any(
                    last_modified_str in part for part in url_parts[index + 1 :]
                ):
                    url_parts.insert(index + 1, last_modified_str)
                    resource["url"] = "/".join(url_parts)
        return resource
