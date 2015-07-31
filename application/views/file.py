from datetime import datetime
import uuid
import os
from application import Module
from application.utils.validator import Validator
from flask import request, send_from_directory, abort
from flask.json import jsonify
import application

module = Module('file', __name__, url_prefix='/file')


@module.get("/<path:filepath>")
def get(filepath):
    path = os.path.join(application.files_folder, os.path.dirname(filepath))
    name = os.path.basename(filepath)
    full_path = os.path.join(path, name)
    mdate = datetime.fromtimestamp(os.stat(full_path).st_mtime)
    delta = datetime.now().date() - mdate.date()

    if filepath.startswith('uploads/') and delta.days > 0:
        os.system('touch %s' % full_path)   # Update modified date
    if os.path.exists(full_path):
        return send_from_directory(path, name)
    else:
        abort(404)


@module.post("/upload")
@module.post("/upload/<ftype>")
def index(ftype=None):
    v = Validator({'file': request.files['file']})
    if ftype == 'image':
        v.field('file').image()
    if v.is_valid():
        file = v.valid_data.file
        ext = file.filename.split('.')[-1]
        uid = str(uuid.uuid4()).replace('-', '')
        directory = os.path.join(application.files_folder, 'uploads')
        if not os.path.exists(directory):
            os.makedirs(directory)
        path = os.path.join(directory, 'file.%s.%s' % (uid, ext))
        v.valid_data.file.save(path)
        return jsonify({'status': 'ok',
                        'file': {
                            'url': '/file/uploads/%s' % os.path.basename(path)
                        }})

    return jsonify({'status': 'fail',
                    'errors': v.errors})
