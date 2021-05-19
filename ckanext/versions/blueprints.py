from ckan import model
from ckan.plugins import toolkit
from flask import Blueprint

from ckanext.versions.logic import action

blueprint = Blueprint(
    'versions',
    __name__,
)


def version_download(id, resource_id, version_id):
    """Download resource blueprint supporting version id.

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
        version = action.version_show(
            context, {'resource_id': resource_id, 'version_id': version_id}
            )
        activity_id = version['activity_id']
    except toolkit.ObjectNotFound:
        toolkit.abort(404, toolkit._(u'Version not found'))

    download_url = toolkit.url_for(
        'resource.download',
        id=id,
        resource_id=resource_id,
        activity_id=activity_id,
        qualified=True
        )
    return toolkit.redirect_to(download_url)


blueprint.add_url_rule(
    u'/dataset/<id>/resource/<resource_id>/version/<version_id>/download',
    view_func=version_download
    )
