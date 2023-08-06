# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os.path

try:
    from urllib.parse import urljoin
except:
    from urlparse import urljoin

from flask import current_app, url_for, request
from werkzeug import secure_filename, FileStorage, cached_property
from werkzeug.utils import import_string


from .backends import BUILTIN_BACKENDS
from .exceptions import UnauthorizedFileType, FileExists, OperationNotSupported
from .files import DEFAULTS, extension, lower_extension


DEFAULT_CONFIG = {
    'allow': DEFAULTS,
    'deny': tuple(),
}

CONF_PREFIX = 'FS_'
PREFIX = '{0}_FS_'


class Config(dict):
    '''
    Wrap the configuration for a single `Storage`.

    Basically, it's an ObjectDict

    # :param destination: The directory to save files to.
    # :param base_url: The URL (ending with a /) that files can be downloaded
    #                  from. If this is `None`, Flask-FS will serve the
    #                  files itself.
    # :param allow: A list of extensions to allow, even if they're not in the
    #               `Storage` extensions list.
    # :param deny: A list of extensions to deny, even if they are in the
    #              `Storage` extensions list.
    '''
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError('Unknown attribute: ' + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError('Unknown attribute: ' + name)


class Storage(object):
    '''
    This represents a single set of files.
    Each Storage is independent of the others.
    This can be reused across multiple application instances,
    as all configuration is stored on the application object itself
    and found with `flask.current_app`.

    :param name:
        The name of this bucket. It defaults to ``files``,
        but you can pick any alphanumeric name you want.
    :param extensions:
        The extensions to allow uploading in this bucket.
        The easiest way to do this is to add together the extension presets
        (for example, ``TEXT + DOCUMENTS + IMAGES``).
        It can be overridden by the configuration with the `{NAME}_BUCKET_ALLOW`
        and `{NAME}_FS__DENY` configuration parameters.
        The default is `DEFAULTS`.
    :param default_dest:
        If given, this should be a callable.
        If you call it with the app,
        it should return the default upload destination path for that app.
    '''

    def __init__(self, name='files', extensions=DEFAULTS, upload_to=None, overwrite=False):
        # if not name.isalnum():
        #     raise ValueError("Name must be alphanumeric (no underscores)")
        self.name = name
        self.extensions = extensions
        self.config = Config()
        self.upload_to = upload_to
        self.backend = None
        self.overwrite = overwrite

    def configure(self, app):
        '''
        Load configuration from application configuration.

        For each storage, the configuration is loaded with the following pattern::

            {STORAGE_NAME}_FS_{KEY}

            # * {STORAGE_NAME}_STORAGE
            # * STORAGES[storage_name]
            # * Default storage configuration

        # Each configuration can be individually overwritten with the following pattern:

        If no configuration is set for a given key, global config is taken as default.
        '''
        prefix = PREFIX.format(self.name.upper())
        config = Config()

        # Set default values
        for key, value in DEFAULT_CONFIG.items():
            config.setdefault(key, value)

        for key, value in app.config.items():
            if key.startswith(prefix):
                config[key.replace(prefix, '').lower()] = value

        backend = config.get('backend', app.config['FS_BACKEND'])
        if backend in BUILTIN_BACKENDS:
            backend_class = import_string(BUILTIN_BACKENDS[backend])
        else:
            backend_class = import_string(backend)
        self.backend = backend_class(self.name, config)
        self.config = config

    @cached_property
    def root(self):
        return self.backend.root

    @property
    def base_url(self):
        config_value = self.config.get('url')
        if config_value:
            return self._clean_url(config_value)
        default_url = current_app.config.get('FS_URL')
        if default_url:
            url = urljoin(default_url, self.name)
            return self._clean_url(url)
        return url_for('fs.get_file', fs=self.name, filename='', _external=True)

    def _clean_url(self, url):
        if not url.startswith('http://') and not url.startswith('https://'):
            url = ('https://' if request.is_secure else 'http://') + url
        if not url.endswith('/'):
            url += '/'
        return url

    @property
    def has_url(self):
        return bool(self.config.get('url') or current_app.config.get('FS_URL'))

    def url(self, filename, external=False):
        '''
        This function gets the URL a file uploaded to this set would be
        accessed at. It doesn't check whether said file exists.

        :param filename: The filename to return the URL for.
        '''
        if filename.startswith('/'):
            filename = filename[1:]
        if self.has_url:
            return self.base_url + filename
        else:
            return url_for('fs.get_file', fs=self.name, filename=filename, _external=external)

    def path(self, filename):
        '''
        This returns the absolute path of a file uploaded to this set. It
        doesn't actually check whether said file exists.

        :param filename: The filename to return the path for.
        :param folder: The subfolder within the upload set previously used
                       to save to.
        '''
        if not self.backend.root:
            raise OperationNotSupported('Direct file access is not supported by ' + self.backend.__class__.__name__)
        return os.path.join(self.backend.root, filename)

    def exists(self, filename):
        '''
        Verify whether a file exists or not.
        '''
        return self.backend.exists(filename)

    def file_allowed(self, storage, basename):
        '''
        This tells whether a file is allowed. It should return `True` if the
        given `werkzeug.FileStorage` object can be saved with the given
        basename, and `False` if it can't. The default implementation just
        checks the extension, so you can override this if you want.

        :param storage: The `werkzeug.FileStorage` to check.
        :param basename: The basename it will be saved under.
        '''
        return self.extension_allowed(extension(basename))

    def extension_allowed(self, ext):
        '''
        This determines whether a specific extension is allowed. It is called
        by `file_allowed`, so if you override that but still want to check
        extensions, call back into this.

        :param ext: The extension to check, without the dot.
        '''
        return ((ext in self.config.allow) or
                (ext in self.extensions and ext not in self.config.deny))

    def read(self, filename):
        '''
        Read a file content.
        '''
        return self.backend.read(filename)

    def open(self, filename):
        '''
        Open the file and return a file-like object.
        '''
        return self.backend.open(filename)

    def write(self, filename, content, overwrite=False):
        '''
        Write content to a file.
        '''
        if not self.overwrite and not overwrite and self.backend.exists(filename):
            raise FileExists()
        return self.backend.write(filename, content)

    def delete(self, filename):
        '''
        Delete a file.
        '''
        return self.backend.delete(filename)

    def save(self, file_or_wfs, filename=None, prefix=None):
        '''
        This saves a `werkzeug.FileStorage` into this storage. If the
        upload is not allowed, an `UploadNotAllowed` error will be raised.
        Otherwise, the file will be saved and its name (including the folder)
        will be returned.

        :param wfs: a `werkzeug.FileStorage` file to save.
        :param folder: The subfolder within the upload set to save to.
        :param name: The name to save the file as. If it ends with a dot, the
                     file's extension will be appended to the end. (If you
                     are using `name`, you can include the folder in the
                     `name` instead of explicitly using `folder`, i.e.
                     ``uset.save(file, name="someguy/photo_123.")``
        '''
        if not filename and isinstance(file_or_wfs, FileStorage):
            filename = lower_extension(secure_filename(file_or_wfs.filename))

        if not filename:
            raise ValueError('filename is required')

        if not self.file_allowed(file_or_wfs, filename):
            raise UnauthorizedFileType()

        if prefix:
            filename = '/'.join((prefix() if callable(prefix) else prefix, filename))

        if self.upload_to:
            filename = '/'.join((self.upload_to() if callable(self.upload_to) else self.upload_to, filename))

        self.backend.save(file_or_wfs, filename)
        return filename

    def __contains__(self, value):
        return self.exists(value)

    def resolve_conflict(self, target_folder, basename):
        '''
        If a file with the selected name already exists in the target folder,
        this method is called to resolve the conflict. It should return a new
        basename for the file.

        The default implementation splits the name and extension and adds a
        suffix to the name consisting of an underscore and a number, and tries
        that until it finds one that doesn't exist.

        :param target_folder: The absolute path to the target.
        :param basename: The file's original basename.
        '''
        name, ext = os.path.splitext(basename)
        count = 0
        while True:
            count = count + 1
            newname = '%s_%d%s' % (name, count, ext)
            if not os.path.exists(os.path.join(target_folder, newname)):
                return newname

    # def load_config(self, app, defaults=None):
    #     '''
    #     This is a helper function for `configure_uploads` that extracts the
    #     configuration for a single set.

    #     :param storage: The upload set.
    #     :param app: The app to load the configuration from.
    #     :param defaults: A dict with keys `url` and `dest` from the
    #                      `UPLOADS_DEFAULT_DEST` and `DEFAULT_UPLOADS_URL`
    #                      settings.
    #     '''
    #     config = app.config
    #     prefix = 'UPLOADED_%s_' % self.name.upper()
    #     using_defaults = False
    #     if defaults is None:
    #         defaults = dict(dest=None, url=None)

    #     allow_extns = tuple(config.get(prefix + 'ALLOW', ()))
    #     deny_extns = tuple(config.get(prefix + 'DENY', ()))
    #     destination = config.get(prefix + 'DEST')
    #     base_url = config.get(prefix + 'URL')

    #     if destination is None:
    #         # the upload set's destination wasn't given
    #         if self.default_dest:
    #             # use the "default_dest" callable
    #             destination = self.default_dest(app)
    #         if destination is None: # still
    #             # use the default dest from the config
    #             if defaults['dest'] is not None:
    #                 using_defaults = True
    #                 destination = os.path.join(defaults['dest'], self.name)
    #             else:
    #                 raise RuntimeError("no destination for set %s" % self.name)

    #     if base_url is None and using_defaults and defaults['url']:
    #         url = defaults['url']
    #         if not url.endswith('/'):
    #             url = url + '/'
    #         base_url = url + self.name + '/'

    #     return StorageConfiguration(destination, base_url, allow_extns, deny_extns)
