import logging
from flask import Blueprint
import ckan.model as model

import ckan.plugins.toolkit as tk
from ckan.views.dataset import _setup_template_variables
from ckan.views.resource import download as downloader

try:
    from ckanext.s3filestore.views.resource import resource_download as s3_downloader
except ImportError:
    from ckan.views.resource import download as downloader

log = logging.getLogger(__name__)
dataset_version = Blueprint("dataset_version", __name__)


def view_dataset(id, version_id):
    context = {
        "for_view": True,
        "auth_user_obj": tk.g.userobj,
    }
    data_dict = {"id": id}

    try:
        pkg_dict = tk.get_action("package_show")(context, data_dict)
        pkg = context["package"]
    except (tk.ObjectNotFound, tk.NotAuthorized):
        return tk.abort(404, tk._("Dataset not found"))

    tk.g.pkg_dict = pkg_dict
    tk.g.pkg = pkg

    try:
        pkg_dict = tk.get_action("package_version_show")(context, {"id": version_id})
    except tk.ObjectNotFound:
        tk.abort(404, tk._("Version not found"))
    except tk.NotAuthorized:
        tk.abort(403, tk._("Unauthorized to view this version"))

    pkg_dict.setdefault("resources", [])

    # can the resources be previewed?
    for resource in pkg_dict["resources"]:
        try:
            resource_views = tk.get_action("resource_view_list")(
                context, {"id": resource["id"]}
            )
            resource["has_views"] = len(resource_views) > 0
        except tk.ObjectNotFound:
            # Resource has been deleted since this version
            resource["has_views"] = False

    package_type = pkg_dict["type"] or "dataset"
    _setup_template_variables(context, {"id": id}, package_type=package_type)

    return tk.render(
        "package/version.html",
        {
            "dataset_type": package_type,
            "pkg_dict": pkg_dict,
            "pkg": pkg,
            "is_versioned": True,
        },
    )


def view_resource(id, resource_id, version_id):
    context = {
        "for_view": True,
        "auth_user_obj": tk.g.userobj,
    }
    try:
        package = tk.get_action("package_show")(context, {"id": id})
    except (tk.ObjectNotFound, tk.NotAuthorized):
        return tk.abort(404, tk._("Dataset not found"))

    try:
        package = tk.get_action("package_version_show")(context, {"id": version_id})
    except tk.ObjectNotFound:
        tk.abort(404, tk._("Version not found"))
    except tk.NotAuthorized:
        tk.abort(403, tk._("Unauthorized to view this version"))

    package.setdefault("resources", [])

    resource = None
    for res in package.get("resources", []):
        if res["id"] == resource_id:
            resource = res
            break
    if not resource:
        return tk.abort(404, tk._("Resource not found"))

    license_id = package.get("license_id")
    try:
        package["isopen"] = model.Package.get_license_register()[license_id].isopen()
    except KeyError:
        package["isopen"] = False

    try:
        resource_views = tk.get_action("resource_view_list")(
            context, {"id": resource["id"]}
        )
        resource["has_views"] = len(resource_views) > 0
    except tk.ObjectNotFound:
        # Resource has been deleted since this version
        resource_views = []
        resource["has_views"] = False

    current_resource_view = None
    view_id = tk.request.args.get("view_id")
    if resource["has_views"]:
        if view_id:
            current_resource_view = [rv for rv in resource_views if rv["id"] == view_id]
            if len(current_resource_view) == 1:
                current_resource_view = current_resource_view[0]
            else:
                return tk.abort(404, tk._("Resource view not found"))
        else:
            current_resource_view = resource_views[0]

    # required for nav menu
    pkg = context["package"]
    dataset_type = pkg.type

    # TODO: remove
    tk.g.package = package
    tk.g.resource = resource
    tk.g.pkg = pkg
    tk.g.pkg_dict = package

    extra_vars = {
        "resource_views": resource_views,
        "current_resource_view": current_resource_view,
        "dataset_type": dataset_type,
        "pkg_dict": package,
        "package": package,
        "resource": resource,
        "pkg": pkg,  # NB it is the current version of the dataset, so ignores
        # activity_id. Still used though in resource views for
        # backward compatibility
    }

    return tk.render("package/resource_version.html", extra_vars)


dataset_version.add_url_rule(
    "/dataset/<id>/version/<version_id>",
    view_func=view_dataset,
    methods=["GET"],
)


dataset_version.add_url_rule(
    "/dataset/<id>/resource/<resource_id>/version/<version_id>",
    view_func=view_resource,
    methods=["GET"],
)


def resource_version_download(package_type, id, resource_id, timestamp, filename):
    """
    Download a specific version of a resource by timestamp.
    """
    # This  use same resource_download function, but includes a timestamp argument
    # to find the correct version of the resource in get_path method.
    if "s3filestore" in tk.config.get("ckan.plugins", ""):

        return s3_downloader(
            package_type=package_type,
            id=id,
            resource_id=resource_id,
            filename=filename,
        )
    else:
        return downloader(
            package_type=package_type,
            id=id,
            resource_id=resource_id,
            filename=filename,
        )


dataset_version.add_url_rule(
    "/dataset/<id>/resource/<resource_id>/download/<timestamp>/<filename>",
    view_func=resource_version_download,
    defaults={"package_type": "dataset"},
    methods=["GET"],
)
