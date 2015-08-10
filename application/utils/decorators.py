from functools import wraps
from flask import g
from werkzeug.exceptions import abort


def requires_permissions(*permissions):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not g.user.is_admin():
                if not set.intersection(g.user.get_permissions(), set(permissions)):
                    return abort(403)
            return f(*args, **kwargs)
        return wrapped
    return wrapper