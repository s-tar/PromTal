__author__ = 'newbie'

import functools

from flask import jsonify


def json():
    """This decorator generates a JSON response from a Python dictionary or
    a SQLAlchemy model."""
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            data = f(*args, **kwargs)
            if isinstance(data, tuple):
                data, status = data
                j = jsonify(data)
                j.status_code = status
                return j
            return jsonify(data)
        return wrapped
    return decorator