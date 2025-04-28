from ckan.plugins import toolkit as tk
from ckanext.versions.model import DatasetVersion


def package_version(key, data, errors, context):
    """
    Validate the package version.
    :param value: The value to validate
    :param context: The context dictionary
    :return: The validated value
    """
    model = context["model"]
    package_id = data.get(("id",))
    current_version = data.get(("version",))
    pkg = model.Package.get(package_id)

    if not pkg:
        return data[key]
    
    previous_version = DatasetVersion.recent_versions(pkg.id)
    if previous_version and current_version == previous_version.name:
        return data.get(key)

    existing_version = DatasetVersion.get(name=current_version, package_id=pkg.id)

    if existing_version:
        return errors[key].append(
            tk._("Version with name '%s' already exists.") % current_version
        )
