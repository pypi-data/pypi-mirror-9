from frasco import current_app, url_for
import os


upload_backends = {}


def file_upload_backend(cls):
    upload_backends[cls.name] = cls
    return cls


class StorageBackend(object):
    def __init__(self, options):
        self.options = options

    def save(self, file, filename):
        raise NotImplementedError

    def url_for(self, filename, **kwargs):
        raise NotImplementedError


@file_upload_backend
class LocalStorageBackend(StorageBackend):
    name = 'local'

    def save(self, file, filename):
        pathname = os.path.join(self.options["upload_dir"], filename)
        dirname = os.path.dirname(pathname)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        file.save(pathname)

    def url_for(self, filename, **kwargs):
        return url_for("static_upload", filename=filename, **kwargs)