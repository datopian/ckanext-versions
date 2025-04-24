
from ckan.plugins import toolkit as tk

def get_package_version_list(package_id):
    """
    Get the package version from the context or data_dict.
    :param context: The context dictionary
    :return: The package version as a string
    """
    context = {
       "ignore_auth": True,
    }
    version_list = tk.get_action("package_version_list")(context, {
        "package_id": package_id,
    })
    return version_list

   