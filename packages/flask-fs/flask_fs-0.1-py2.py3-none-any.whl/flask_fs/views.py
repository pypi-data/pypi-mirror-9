# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import send_from_directory, abort, Blueprint


from . import by_name

bp = Blueprint('fs', __name__)


@bp.route('/<string:fs>/<path:filename>')
def get_file(fs, filename):
    '''Serve files for storages with direct file access'''
    storage = by_name(fs)
    if storage is None:
        abort(404)
    if not storage.root or not storage.exists(filename):
        abort(404)
    return send_from_directory(storage.root, filename)
