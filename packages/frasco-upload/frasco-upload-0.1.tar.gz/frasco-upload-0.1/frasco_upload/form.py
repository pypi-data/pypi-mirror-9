from wtforms import FileField as BaseFileField, ValidationError
from flask_wtf.file import FileRequired
from werkzeug import FileStorage
from frasco import current_app
import os
import uuid


class FileField(BaseFileField):
    def __init__(self, label=None, validators=None, auto_save=True, upload_dir=None, upload_backend=None,\
                 uuid_prefix=None, keep_filename=None, subfolders=None, backend_in_filename=True, **kwargs):
        super(FileField, self).__init__(label, validators, **kwargs)
        self.file = None
        self.auto_save = auto_save
        self.upload_dir = upload_dir
        self._upload_backend = upload_backend
        self.uuid_prefix = uuid_prefix
        self.keep_filename = keep_filename
        self.subfolders = subfolders
        self.backend_in_filename = backend_in_filename

    @property
    def upload_backend(self):
        return current_app.features.upload.get_backend(self._upload_backend)

    def process_formdata(self, valuelist):
        if not valuelist:
            return
        self.file = valuelist[0]
        self.data = None
        self.filename = None
        if not self.has_file():
            return

        self.filename = current_app.features.upload.generate_filename(self.file.filename,
            uuid_prefix, keep_filename, subfolders)
        if self.upload_dir:
            self.filename = os.path.join(self.upload_dir, self.filename)
        if self.backend_in_filename:
            self.data = self.upload_backend.name + '://' + self.filename
        else:
            self.data = self.filename
        if self.auto_save:
            self.save_file()

    def save_file(self):
        self.upload_backend.save(self.file, self.filename)

    def has_file(self):
        # compatibility with Flask-WTF
        if not isinstance(self.file, FileStorage):
            return False
        return self.file.filename not in [None, '', '<fdopen>']


class FileAllowed(object):
    def __init__(self, extensions, message=None):
        self.extensions = extensions
        self.message = message

    def __call__(self, form, field):
        if not field.has_file():
            return

        filename = field.file.filename.lower()
        ext = filename.rsplit('.', 1)[-1]
        if ext in self.extensions:
            return

        message = self.message
        if message is None:
            message = field.gettext("File type not allowed")
        raise ValidationError(message)