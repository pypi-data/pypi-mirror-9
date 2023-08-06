from frasco import Feature, current_app, action
from .backends import upload_backends, StorageBackend
from werkzeug import secure_filename
from flask import send_from_directory
import uuid
import os
from tempfile import NamedTemporaryFile


class UploadFeature(Feature):
    name = 'upload'
    defaults = {"default_backend": "local",
                "upload_dir": "uploads",
                "upload_url": "/uploads",
                "uuid_prefixes": True,
                "keep_filenames": True,
                "subfolders": False}

    def init_app(self, app):
        self.backends = {}
        app.add_template_global(url_for_upload)

        def send_uploaded_file(filename):
            return send_from_directory(self.options["upload_dir"], filename,
                cache_timeout=app.config['SEND_FILE_MAX_AGE_DEFAULT'])
        app.add_url_rule(self.options["upload_url"] + "/<path:filename>",
                         endpoint="static_upload",
                         view_func=send_uploaded_file)

    def get_backend(self, name=None):
        if isinstance(name, StorageBackend):
            return name
        if name is None:
            name = self.options['default_backend']
        if name not in self.backends:
            if name not in upload_backends:
                raise Exception("Upload backend '%s' does not exist" % name)
            self.backends[name] = upload_backends[name](self.options)
        return self.backends[name]

    def get_backend_from_filename(self, filename):
        if '://' in filename:
            return filename.split('://', 1)
        return None, filename

    @action(default_option='filename')
    def generate_filename(self, filename, uuid_prefix=None, keep_filename=None, subfolders=None):
        if uuid_prefix is None:
            uuid_prefix = self.options["uuid_prefixes"]
        if keep_filename is None:
            keep_filename = self.options["keep_filenames"]
        if subfolders is None:
            subfolders = self.options["subfolders"]

        if uuid_prefix and not keep_filename:
            _, ext = os.path.splitext(filename)
            filename = str(uuid.uuid4()) + ext
        else:
            filename = secure_filename(filename)
            if uuid_prefix:
                filename = str(uuid.uuid4()) + "-" + filename

        if subfolders:
            if uuid_prefix:
                parts = filename.split("-", 4)
                filename = os.path.join(os.path.join(*parts[:4]), filename)
            else:
                filename = os.path.join(os.path.join(*filename[:4]), filename)

        return filename

    @action(default_option='file')
    def save_uploaded_file_temporarly(self, file):
        tmp = NamedTemporaryFile(delete=False)
        tmp.close()
        file.save(tmp.name)
        return tmp.name


def url_for_upload(filename, backend=None, **kwargs):
    if backend is None:
        backend, filename = current_app.features.upload.get_backend_from_filename(filename)
    backend = current_app.features.upload.get_backend(backend)
    return backend.url_for(filename, **kwargs)


try:
    import frasco_forms.form
    import form
    frasco_forms.form.field_type_map.update({
        "upload": form.FileField})
except ImportError:
    pass