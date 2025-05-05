import os
import datetime
import ckan.plugins.toolkit as toolkit
from flask import has_request_context

from ckan.lib.uploader import ResourceUpload as DefaultResourceUpload


def _get_stringified_date(lastmodified):
    if isinstance(lastmodified, datetime.datetime):
        last_modified_str = lastmodified.strftime("%Y-%m-%d-%H-%M-%S")
    else:
        last_modified_str = (
            str(lastmodified)
            .replace(":", "-")
            .replace("T", "-")
            .replace(" ", "-")
            .split(".")[0]
        )
    return last_modified_str


try:
    from ckanext.s3filestore.uploader import S3ResourceUploader

    class S3ResourceUpload(S3ResourceUploader):
        def __init__(self, resource):
            super().__init__(resource)
            self.resource = resource

        def get_path(self, id, filename):
            if self.resource and self.resource.get("last_modified", None):
                last_modified_str = _get_stringified_date(
                    self.resource.get("last_modified")
                )
                if has_request_context():
                    request_timestamp = toolkit.request.view_args.get("timestamp")
                else:
                    request_timestamp = None

                last_modified_str = request_timestamp or last_modified_str
                base_directory = self.get_directory(id, self.storage_path)
                directory = os.path.join(base_directory, last_modified_str)
            return os.path.join(directory, filename)

except ImportError:
    S3ResourceUpload = None


class LocalResourceUpload(DefaultResourceUpload):
    """A local resource uploader that takes revisions into account"""

    def __init__(self, data_dict):
        super(LocalResourceUpload, self).__init__(data_dict)
        self.resource = data_dict

    def get_path(self, id, filename=None):
        filepath = super(LocalResourceUpload, self).get_path(id)
        if self.resource and self.resource.get("last_modified", None):
            if has_request_context():
                request_timestamp = toolkit.request.view_args.get("timestamp")
            else:
                request_timestamp = None
            last_modified_str = _get_stringified_date(self.resource["last_modified"])
            last_modified_str = request_timestamp or last_modified_str
            filepath = "-".join([filepath, last_modified_str])
        return filepath

    def upload(self, *args, **kwargs):
        self.clear = False
        return super(LocalResourceUpload, self).upload(*args, **kwargs)
