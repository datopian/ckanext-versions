from ckan import model
from ckan.plugins import toolkit
from flask import Blueprint

from ckanext.versions.logic import action

blueprint = Blueprint(
    'versions',
    __name__,
)


def version_download(id, resource_id, version):
    """Download resource blueprint supporting version name.

    This download blueprint gets the activity_id from the version and redirects
    to a download url that can handle it. Currently is working with
    blob_storage extension but can work with any download endpoint that knows
    how to handle activities for resources.
    """
    context = {
        'model': model,
        'user': toolkit.c.user
    }

    try:
        activity_id = action.get_activity_id_from_resource_version_name(
            context, {'resource_id': resource_id, 'version_name': version})
    except toolkit.NotFound:
        toolkit.abort(404, toolkit._(u'Activity not found'))

    download_url = toolkit.url_for(
        'resource.download',
        id=id,
        resource_id=resource_id,
        activity_id=activity_id,
        qualified=True
        )
    return toolkit.redirect_to(download_url)


blueprint.add_url_rule(
    u'/dataset/<id>/resource/<resource_id>/version/<version>/download',
    view_func=version_download
    )
