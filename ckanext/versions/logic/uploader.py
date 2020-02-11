"""Patched uploader supporting file revisioning
"""
import logging

import ckan.plugins as plugins
from ckan.lib.uploader import ResourceUpload

UPLOAD_TS_FIELD = 'versions_upload_timestamp'

log = logging.getLogger(__name__)


def get_uploader(this_plugin, data_dict):
    """This is somewhat copied from ckan.lib.uploader logic

    Generate an uploader object and return it; We wrap uploader instantiation
    with this factory function, to support cases where a custom uploader has
    been enabled; In such cases, we will not override it, and it is expected
    that this uploader will support per-revision storage.
    """
    upload = None
    for plugin in plugins.PluginImplementations(plugins.IUploader):
        if plugin is this_plugin:
            continue
        upload = plugin.get_resource_uploader(data_dict)

    # default uploader
    if upload is None:
        upload = LocalResourceUpload(data_dict)

    log.debug("Wrapping Uploader from %s", upload.__class__.__name__)
    return upload


class LocalResourceUpload(ResourceUpload):
    """A local resource uploader that takes revisions into account
    """
    def __init__(self, data_dict):
        super(LocalResourceUpload, self).__init__(data_dict)
        self.resource_metadata = data_dict

    def get_path(self, id):
        filepath = super(LocalResourceUpload, self).get_path(id)
        if self.resource_metadata and \
                self.resource_metadata.get(UPLOAD_TS_FIELD, None):
            modified_ts = self.resource_metadata[UPLOAD_TS_FIELD]
            if hasattr(modified_ts, 'isoformat'):
                modified_ts = modified_ts.isoformat()
            filepath = '-'.join([filepath, modified_ts])
        log.debug("Computed resource path is %s", filepath)
        return filepath

    def upload(self, *args, **kwargs):
        self.clear = False
        return super(LocalResourceUpload, self).upload(*args, **kwargs)
