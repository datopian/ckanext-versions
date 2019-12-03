from ckan import model
from ckan.plugins import toolkit
from flask import Blueprint

versions = Blueprint('versions', __name__)


def changes(id):
    context = {
        'model': model, 'user': toolkit.c.user
    }

    try:
        # We'll need this for the title / breadcrumbs, etc
        current_pkg_dict = toolkit.get_action('package_show')(
            context, {'id': id})
    except toolkit.NotAuthorized:
        toolkit.abort(401, 'Not authorized to read dataset')

    versions = toolkit.get_action('dataset_version_list')(
        context, {'dataset': id})

    version_id_1 = toolkit.request.args.get('version_id_1')
    version_id_2 = toolkit.request.args.get('version_id_2')

    if version_id_1 and version_id_2:
        diff = toolkit.get_action('dataset_versions_diff')(
            context, {
                'version_id_1': version_id_1,
                'version_id_2': version_id_2,
                'diff_type': 'html',
            }
        )
    else:
        diff = None

    return toolkit.render(
        'package/version_changes.html', {
            'diff': diff,
            'pkg_dict': current_pkg_dict,
            'versions': versions,
            'version_id_1': version_id_1,
            'version_id_2': version_id_2,
        }
    )


versions.add_url_rule('/dataset/<id>/version/changes', view_func=changes)
